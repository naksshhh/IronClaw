"""
Unified Execution Service for Iron Claw.

Handles command execution with:
1. Primary: MobileRun Cloud (if configured)
2. Fallback: Local DroidRun CLI (if device connected via ADB)
"""
import asyncio
import logging
import subprocess
import shutil
import time
from typing import Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("ironclaw.services.execution")


class ExecutionBackend(str, Enum):
    """Available execution backends."""
    MOBILERUN_CLOUD = "mobilerun_cloud"
    DROIDRUN_LOCAL = "droidrun_local"
    NONE = "none"


_TERMINAL_TASK_STATES = {"completed", "failed", "cancelled"}


def adb_device_attached(adb_stdout: str) -> bool:
    """True when `adb devices` lists at least one device in the ready state."""
    lines = adb_stdout.splitlines()
    for line in lines[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            return True
    return False


def constrain_command(command: str, packages: Optional[list[str]]) -> str:
    """Tell the cloud agent which packages it is allowed to open."""
    allowed = [pkg for pkg in (packages or []) if pkg]
    if not allowed:
        return command
    return (
        f"{command}\n\n"
        "Security constraint: only open or interact with these Android packages: "
        f"{', '.join(allowed)}. If any other package is in the foreground, press Home and stop."
    )


@dataclass
class ExecutionResult:
    """Result from command execution."""
    success: bool
    backend: ExecutionBackend
    output: Optional[str] = None
    error: Optional[str] = None
    task_id: Optional[str] = None
    screenshots: list[str] = None
    steps: int = 0

    def __post_init__(self):
        if self.screenshots is None:
            self.screenshots = []


class ExecutionService:
    """
    Unified execution service for mobile automation.

    Automatically selects the best available backend:
    1. MobileRun Cloud - if API key and device ID are configured
    2. DroidRun Local - if a phone is connected via ADB

    Usage:
        service = ExecutionService(
            mobilerun_api_key="...",
            mobilerun_device_id="...",
        )

        # Check available backends
        backend = await service.get_available_backend()

        # Execute command
        result = await service.execute("Open settings and increase font size")
    """

    def __init__(
        self,
        mobilerun_api_key: Optional[str] = None,
        mobilerun_device_id: Optional[str] = None,
        mobilerun_base_url: str = "https://api.mobilerun.ai",
        local_device_serial: Optional[str] = None,
        prefer_local: bool = False,
        allowed_packages: Optional[list[str]] = None,
        task_timeout: float = 300.0,
        poll_interval: float = 2.0,
    ):
        """
        Initialize execution service.

        Args:
            mobilerun_api_key: MobileRun Cloud API key
            mobilerun_device_id: MobileRun device ID
            mobilerun_base_url: MobileRun API URL
            local_device_serial: Local ADB device serial (optional)
            prefer_local: If True, prefer local DroidRun over cloud
            allowed_packages: Android packages the agent may open
            task_timeout: How long to wait for a cloud task to finish
            poll_interval: Seconds between cloud task status checks
        """
        self.mobilerun_api_key = mobilerun_api_key
        self.mobilerun_device_id = mobilerun_device_id
        self.mobilerun_base_url = mobilerun_base_url
        self.local_device_serial = local_device_serial
        self.prefer_local = prefer_local
        self.allowed_packages = list(allowed_packages or [])
        self.task_timeout = task_timeout
        self.poll_interval = poll_interval

        self._mobilerun_client = None
        self._backend_cache: Optional[ExecutionBackend] = None

    def _get_mobilerun_client(self):
        """Get or create MobileRun client."""
        if self._mobilerun_client is None and self.mobilerun_api_key:
            from ironclaw_mobilerun import MobileRunClient
            self._mobilerun_client = MobileRunClient(
                api_key=self.mobilerun_api_key,
                base_url=self.mobilerun_base_url,
            )
        return self._mobilerun_client

    async def check_mobilerun_available(self) -> bool:
        """Check if MobileRun Cloud is available."""
        if not self.mobilerun_api_key or not self.mobilerun_device_id:
            return False

        try:
            client = self._get_mobilerun_client()
            if client:
                return await client.ping()
        except Exception as e:
            logger.warning(f"MobileRun not available: {e}")
        return False

    async def check_droidrun_available(self) -> bool:
        """Check whether adb sees a device. This does not run a command on the phone."""
        if shutil.which("adb") is None:
            logger.info("adb not found in PATH")
            return False

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["adb", "devices"],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except subprocess.TimeoutExpired:
            logger.warning("adb devices timed out")
            return False
        except Exception as e:
            logger.warning(f"adb devices failed: {e}")
            return False

        if result.returncode != 0:
            logger.info("adb devices failed: %s", result.stderr.strip())
            return False
        return adb_device_attached(result.stdout)

    async def get_available_backend(self, force_refresh: bool = False) -> ExecutionBackend:
        """
        Determine the best available backend.

        Returns:
            ExecutionBackend enum indicating which backend to use
        """
        if self._backend_cache and not force_refresh:
            return self._backend_cache

        # Check backends based on preference
        if self.prefer_local:
            if await self.check_droidrun_available():
                self._backend_cache = ExecutionBackend.DROIDRUN_LOCAL
                return self._backend_cache
            if await self.check_mobilerun_available():
                self._backend_cache = ExecutionBackend.MOBILERUN_CLOUD
                return self._backend_cache
        else:
            if await self.check_mobilerun_available():
                self._backend_cache = ExecutionBackend.MOBILERUN_CLOUD
                return self._backend_cache
            if await self.check_droidrun_available():
                self._backend_cache = ExecutionBackend.DROIDRUN_LOCAL
                return self._backend_cache

        self._backend_cache = ExecutionBackend.NONE
        return self._backend_cache

    async def execute(
        self,
        command: str,
        max_steps: int = 15,
        vision: bool = True,
        reasoning: bool = False,
        llm_model: Optional[str] = None,
        force_backend: Optional[ExecutionBackend] = None,
    ) -> ExecutionResult:
        """
        Execute a natural language command.

        Args:
            command: Natural language command to execute
            max_steps: Maximum execution steps
            vision: Enable vision mode (screenshots)
            reasoning: Enable reasoning/planning mode
            llm_model: LLM model to use (for MobileRun Cloud)
            force_backend: Force a specific backend (optional)

        Returns:
            ExecutionResult with success status and output
        """
        backend = force_backend or await self.get_available_backend()

        logger.info(f"Executing on {backend.value}: {command[:50]}...")

        if backend == ExecutionBackend.MOBILERUN_CLOUD:
            return await self._execute_mobilerun(command, max_steps, vision, reasoning, llm_model)
        elif backend == ExecutionBackend.DROIDRUN_LOCAL:
            return await self._execute_droidrun(command, max_steps, vision, reasoning)
        else:
            return ExecutionResult(
                success=False,
                backend=ExecutionBackend.NONE,
                error="No execution backend available. Connect a device or configure MobileRun.",
            )

    async def _execute_mobilerun(
        self,
        command: str,
        max_steps: int,
        vision: bool,
        reasoning: bool,
        llm_model: Optional[str] = None,
    ) -> ExecutionResult:
        """Create a MobileRun task and wait until it finishes."""
        try:
            client = self._get_mobilerun_client()
            if client is None:
                return ExecutionResult(
                    success=False,
                    backend=ExecutionBackend.MOBILERUN_CLOUD,
                    error="MobileRun client is not configured",
                )
            task = await client.run_task(
                device_id=self.mobilerun_device_id,
                command=constrain_command(command, self.allowed_packages),
                max_steps=max_steps,
                vision=vision,
                reasoning=reasoning,
                llm_model=llm_model,
                apps=self.allowed_packages or None,
            )
            return await self._await_mobilerun_task(client, task.task_id)
        except Exception as e:
            logger.error(f"MobileRun execution failed: {e}", exc_info=True)
            return ExecutionResult(
                success=False,
                backend=ExecutionBackend.MOBILERUN_CLOUD,
                error="MobileRun execution failed",
            )

    async def _await_mobilerun_task(self, client, task_id: str) -> ExecutionResult:
        """Poll until the task is completed, failed, cancelled, or timed out.

        Creating a task is not success. The caller only hears success after
        the status endpoint reports completed.
        """
        deadline = time.monotonic() + self.task_timeout
        last_state = "pending"
        while True:
            status = await client.get_task_status(task_id)
            raw_state = getattr(status, "status", "")
            state = raw_state.value if hasattr(raw_state, "value") else str(raw_state)
            last_state = state.lower()
            if last_state in _TERMINAL_TASK_STATES:
                succeeded = last_state == "completed"
                result = getattr(status, "result", None)
                return ExecutionResult(
                    success=succeeded,
                    backend=ExecutionBackend.MOBILERUN_CLOUD,
                    output=str(result) if succeeded and result is not None else ("Task completed." if succeeded else None),
                    error=None if succeeded else (getattr(status, "error", None) or f"Task {last_state}"),
                    task_id=task_id,
                    steps=int(getattr(status, "progress", 0) or 0),
                )
            if time.monotonic() >= deadline:
                return ExecutionResult(
                    success=False,
                    backend=ExecutionBackend.MOBILERUN_CLOUD,
                    error=f"Task {task_id} still {last_state} after {self.task_timeout}s",
                    task_id=task_id,
                )
            await asyncio.sleep(self.poll_interval)

    async def _execute_droidrun(
        self,
        command: str,
        max_steps: int,
        vision: bool,
        reasoning: bool,
    ) -> ExecutionResult:
        """Execute via local DroidRun CLI."""
        try:
            cmd = ["droidrun", "run", command, "--steps", str(max_steps)]

            if vision:
                cmd.append("--vision")
            if reasoning:
                cmd.append("--reasoning")
            if self.local_device_serial:
                cmd.extend(["--device", self.local_device_serial])

            result = await asyncio.to_thread(
                subprocess.run,
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            success = result.returncode == 0
            output = result.stdout if success else result.stderr

            return ExecutionResult(
                success=success,
                backend=ExecutionBackend.DROIDRUN_LOCAL,
                output=output,
                error=result.stderr if not success else None,
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                backend=ExecutionBackend.DROIDRUN_LOCAL,
                error="Command execution timed out (300s)",
            )
        except Exception as e:
            logger.error(f"DroidRun execution failed: {e}")
            return ExecutionResult(
                success=False,
                backend=ExecutionBackend.DROIDRUN_LOCAL,
                error=str(e),
            )

    async def execute_stream(
        self,
        command: str,
        max_steps: int = 15,
        vision: bool = True,
        reasoning: bool = False,
        llm_model: Optional[str] = None,
    ) -> AsyncIterator[dict]:
        """
        Execute with streaming updates (MobileRun only).

        Yields status updates as the task progresses.
        Falls back to non-streaming for DroidRun.
        """
        backend = await self.get_available_backend()

        if backend == ExecutionBackend.MOBILERUN_CLOUD:
            client = self._get_mobilerun_client()
            async for update in client.run_task_stream(
                device_id=self.mobilerun_device_id,
                command=command,
                max_steps=max_steps,
                vision=vision,
                reasoning=reasoning,
                llm_model=llm_model,
            ):
                yield update
        else:
            # For DroidRun, execute and yield single result
            result = await self.execute(command, max_steps, vision, reasoning, llm_model)
            yield {
                "status": "completed" if result.success else "failed",
                "output": result.output,
                "error": result.error,
            }

    async def take_screenshot(self) -> Optional[str]:
        """Take a screenshot from the current device."""
        backend = await self.get_available_backend()

        if backend == ExecutionBackend.MOBILERUN_CLOUD:
            client = self._get_mobilerun_client()
            return await client.take_screenshot(self.mobilerun_device_id)
        elif backend == ExecutionBackend.DROIDRUN_LOCAL:
            # Use ADB to take screenshot
            try:
                result = await asyncio.to_thread(
                    subprocess.run,
                    ["adb", "shell", "screencap", "-p"],
                    capture_output=True,
                    timeout=30,
                )
                if result.returncode == 0:
                    import base64
                    return base64.b64encode(result.stdout).decode()
            except Exception as e:
                logger.error(f"Screenshot failed: {e}")
        return None


# Singleton instance
_service_instance: Optional[ExecutionService] = None


def _allowed_packages_from_config() -> list[str]:
    try:
        from ..utils.config import get_app_config
        return list(get_app_config().safe_packages)
    except Exception:
        return []


def get_execution_service() -> ExecutionService:
    """Get the singleton execution service."""
    global _service_instance
    if _service_instance is None:
        # Load from environment
        import os
        _service_instance = ExecutionService(
            mobilerun_api_key=os.getenv("MOBILERUN_API_KEY"),
            mobilerun_device_id=os.getenv("MOBILERUN_DEVICE_ID"),
            local_device_serial=os.getenv("DEVICE_SERIAL"),
            prefer_local=os.getenv("PREFER_LOCAL_DEVICE", "false").lower() == "true",
            allowed_packages=_allowed_packages_from_config(),
        )
    return _service_instance


def configure_execution_service(
    mobilerun_api_key: Optional[str] = None,
    mobilerun_device_id: Optional[str] = None,
    local_device_serial: Optional[str] = None,
    prefer_local: bool = False,
) -> ExecutionService:
    """Configure and return the execution service."""
    global _service_instance
    _service_instance = ExecutionService(
        mobilerun_api_key=mobilerun_api_key,
        mobilerun_device_id=mobilerun_device_id,
        local_device_serial=local_device_serial,
        prefer_local=prefer_local,
    )
    return _service_instance
