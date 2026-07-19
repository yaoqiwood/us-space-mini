import { API_BASE_URL } from "../config";

export class ApiError extends Error {
  constructor(
    public readonly statusCode: number,
    message: string,
  ) {
    super(message);
  }
}

export function request<T>(
  path: string,
  method: WechatMiniprogram.RequestOption["method"] = "GET",
  data?: Record<string, unknown>,
  authenticated = true,
): Promise<T> {
  return new Promise((resolve, reject) => {
    const token = wx.getStorageSync("access_token");
    wx.request({
      url: `${API_BASE_URL}${path}`,
      method,
      data,
      header: authenticated && token ? { Authorization: `Bearer ${token}` } : {},
      success: (response) => {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data as T);
          return;
        }
        const detail = (response.data as { detail?: string } | undefined)?.detail;
        reject(new ApiError(response.statusCode, detail || `Request failed with status ${response.statusCode}`));
      },
      fail: reject,
    });
  });
}
