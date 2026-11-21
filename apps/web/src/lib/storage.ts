import type { ChatThread } from "@/types/chat";

const STORAGE_KEY = "ironclaw.threads";

export function loadThreads(): ChatThread[] {
  if (typeof localStorage === "undefined") {
    return [];
  }
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return [];
    }
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function saveThreads(threads: ChatThread[]): void {
  if (typeof localStorage === "undefined") {
    return;
  }
  const stored = threads.map((thread) => ({
    ...thread,
    draftAttachments: (thread.draftAttachments ?? []).map(({ previewUrl: _preview, ...attachment }) => attachment),
    messages: thread.messages.map((message) => ({
      ...message,
      attachments: message.attachments?.map(({ previewUrl: _preview, ...attachment }) => attachment),
    })),
  }));
  localStorage.setItem(STORAGE_KEY, JSON.stringify(stored));
}
