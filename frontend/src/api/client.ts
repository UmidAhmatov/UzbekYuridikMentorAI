const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "/api";

type ApiErrorPayload = {
  detail?: string;
  error_code?: string;
};

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  timeoutMs = 120_000,
): Promise<T> {
  const controller = new AbortController();
  const timeout = window.setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      ...options,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
    });
    if (!response.ok) {
      const error = (await response.json().catch(() => null)) as ApiErrorPayload | null;
      throw new Error(error?.detail || `Server xatosi (HTTP ${response.status}).`);
    }
    return response.json() as Promise<T>;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new Error("So'rov vaqti tugadi. Qayta urinib ko'ring.");
    }
    throw error;
  } finally {
    window.clearTimeout(timeout);
  }
}

export function resolveApiUrl(path: string): string {
  if (/^https?:\/\//.test(path)) {
    return path;
  }
  if (path.startsWith("/api") && apiBaseUrl !== "/api") {
    return `${apiBaseUrl}${path.slice(4)}`;
  }
  return path;
}

export function getApiBaseUrl(): string {
  return apiBaseUrl;
}

