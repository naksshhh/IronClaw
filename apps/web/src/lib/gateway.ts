const configured = import.meta.env.VITE_GATEWAY_URL || "http://localhost:8000";

export const GATEWAY_HTTP = configured.replace(/\/$/, "");
export const GATEWAY_WS = GATEWAY_HTTP.replace(/^http/, "ws");

export function authHeaders(extra?: HeadersInit): Headers {
  const headers = new Headers(extra);
  const token = import.meta.env.VITE_IRONCLAW_API_TOKEN;
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  return headers;
}

export function withToken(url: string): string {
  const token = import.meta.env.VITE_IRONCLAW_API_TOKEN;
  if (!token) {
    return url;
  }
  const next = new URL(url);
  next.searchParams.set("token", token);
  return next.toString();
}
