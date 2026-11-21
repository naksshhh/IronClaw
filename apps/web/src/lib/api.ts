import { GATEWAY_HTTP, authHeaders } from "./gateway";

async function send(path: string, init: RequestInit = {}) {
  const headers = authHeaders(init.headers);
  const isForm = typeof FormData !== "undefined" && init.body instanceof FormData;
  if (!isForm && init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(`${GATEWAY_HTTP}${path}`, { ...init, headers });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail || data.error || data.message || response.statusText;
    throw new Error(typeof detail === "string" ? detail : "Request failed");
  }
  return data;
}

export const api = {
  health: () => send("/health"),

  chat: (message: string, imageFilename?: string, llmModel?: string, mode?: "local" | "cloud") =>
    send("/api/chat", {
      method: "POST",
      body: JSON.stringify({
        message,
        image_filename: imageFilename,
        llm_model: llmModel,
        mode: mode || "local",
      }),
    }),

  chatCloud: (message: string, llmModel?: string, options?: { deviceId?: string }) =>
    send("/api/chat-cloud", {
      method: "POST",
      body: JSON.stringify({
        message,
        llm_model: llmModel,
        device_id: options?.deviceId,
        wait_for_completion: false,
      }),
    }),

  chatCloudTasks: (taskId: string) => send(`/api/chat-cloud/tasks/${taskId}`),

  upload: async (file: File) => {
    const body = new FormData();
    body.append("file", file);
    return send("/api/upload", { method: "POST", body });
  },

  checkAndroidVersion: () => send("/api/v1/tabs/test/check-android-version", { method: "POST" }),
  tabsList: () => send("/api/v1/tabs/list"),
  tabsOrganize: () => send("/api/v1/tabs/organize", { method: "POST" }),
  tabsCloseOld: (days: number) =>
    send("/api/v1/tabs/close-old", {
      method: "POST",
      body: JSON.stringify({ days_old: days }),
    }),
  tabsMergeDuplicates: () => send("/api/v1/tabs/merge-duplicates", { method: "POST" }),
  tabsSessions: () => send("/api/v1/tabs/sessions"),
  tabsStatus: (taskId: string) => send(`/api/v1/tabs/status/${taskId}`),

  jobPortals: () =>
    send("/api/job-portals").catch(() =>
      fetch("http://127.0.0.1:5123/api/job-portals", { headers: authHeaders() }).then(async (response) => {
        const data = await response.json().catch(() => ({}));
        if (!response.ok) {
          throw new Error(data.error || "Job hunter is not running");
        }
        return data;
      }),
    ),
};
