"""Cloud execution waits for completion, and device checks do not drive the phone."""

import pytest

from ironclaw.services.execution_service import (
    ExecutionService,
    adb_device_attached,
    constrain_command,
)


def test_adb_listing_requires_a_ready_device():
    assert adb_device_attached("List of devices attached\nemulator-5554\tdevice\n") is True
    assert adb_device_attached("List of devices attached\n") is False
    assert adb_device_attached("List of devices attached\nemulator-5554\toffline\n") is False


def test_constraint_names_the_allowed_packages():
    command = constrain_command("Open Chrome", ["com.android.chrome"])
    assert "com.android.chrome" in command
    assert command.startswith("Open Chrome")
    assert constrain_command("Open Chrome", []) == "Open Chrome"


@pytest.mark.asyncio
async def test_availability_check_runs_adb_devices_only(monkeypatch):
    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(list(cmd))

        class Result:
            returncode = 0
            stdout = "List of devices attached\n"
            stderr = ""

        return Result()

    monkeypatch.setattr(
        "ironclaw.services.execution_service.shutil.which",
        lambda name: "/usr/bin/adb" if name == "adb" else None,
    )
    monkeypatch.setattr("ironclaw.services.execution_service.subprocess.run", fake_run)

    service = ExecutionService()
    assert await service.check_droidrun_available() is False
    assert calls == [["adb", "devices"]]
    assert all("droidrun" not in part for call in calls for part in call)


class _Status:
    def __init__(self, status, result=None, error=None, progress=0):
        self.status = status
        self.result = result
        self.error = error
        self.progress = progress


class _Task:
    task_id = "task-1"


class _Client:
    def __init__(self, statuses):
        self.statuses = list(statuses)
        self.task_kwargs = None

    async def run_task(self, **kwargs):
        self.task_kwargs = kwargs
        return _Task()

    async def get_task_status(self, task_id):
        assert task_id == "task-1"
        return self.statuses.pop(0)


@pytest.mark.asyncio
async def test_creating_a_task_is_not_success():
    client = _Client([_Status("pending")])
    service = ExecutionService(
        mobilerun_api_key="key",
        mobilerun_device_id="device",
        task_timeout=0,
        poll_interval=0,
    )
    service._mobilerun_client = client

    result = await service._execute_mobilerun("Open settings", 30, True, False)

    assert result.success is False
    assert result.task_id == "task-1"
    assert "created successfully" not in (result.output or "").lower()
    assert "still pending" in (result.error or "")


@pytest.mark.asyncio
async def test_success_waits_until_the_task_completes():
    client = _Client([
        _Status("pending"),
        _Status("completed", result="Opened settings", progress=4),
    ])
    service = ExecutionService(
        mobilerun_api_key="key",
        mobilerun_device_id="device",
        allowed_packages=["com.android.settings"],
        task_timeout=2,
        poll_interval=0.01,
    )
    service._mobilerun_client = client

    result = await service._execute_mobilerun("Open settings", 30, True, False)

    assert result.success is True
    assert result.output == "Opened settings"
    assert result.steps == 4
    assert client.task_kwargs["apps"] == ["com.android.settings"]
    assert "com.android.settings" in client.task_kwargs["command"]
