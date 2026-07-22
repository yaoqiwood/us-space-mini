import { API_BASE_URL } from "../config";

type HttpMethod = NonNullable<WechatMiniprogram.RequestOption["method"]>;

export interface ApiRequestOptions {
  method?: HttpMethod;
  data?: Record<string, unknown>;
  authenticated?: boolean;
  timeout?: number;
}

export class ApiError extends Error {
  constructor(
    public readonly statusCode: number,
    message: string,
    public readonly details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

function getErrorMessage(data: unknown, fallback: string): string {
  if (typeof data === "string" && data) {
    return data;
  }
  if (!data || typeof data !== "object") {
    return fallback;
  }

  const detail = (data as { detail?: unknown }).detail;
  if (typeof detail === "string" && detail) {
    return detail;
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => (item && typeof item === "object" ? (item as { msg?: unknown }).msg : ""))
      .filter((message): message is string => typeof message === "string" && Boolean(message));
    if (messages.length) {
      return messages.join("; ");
    }
  }
  return fallback;
}

function buildUrl(path: string): string {
  return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}

export function request<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const {
    method = "GET",
    data,
    authenticated = true,
    timeout = 10_000,
  } = options;

  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync("access_token");
    wx.request({
      url: buildUrl(path),
      method,
      data,
      timeout,
      header: {
        "content-type": "application/json",
        ...(authenticated && token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success: (response) => {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data as T);
          return;
        }
        reject(new ApiError(
          response.statusCode,
          getErrorMessage(response.data, `Request failed with status ${response.statusCode}`),
          response.data,
        ));
      },
      fail: (error) => {
        reject(new ApiError(0, error.errMsg || "Network request failed", error));
      },
    });
  });
}

export function checkApiHealth(): Promise<{ status: string }> {
  return request<{ status: string }>("/health", { authenticated: false });
}

export interface EntryProbeResponse {
  status: "ok";
  message: string;
}

export function probeEntryService(): Promise<EntryProbeResponse> {
  return request<EntryProbeResponse>("/entry/probe", { authenticated: false });
}
