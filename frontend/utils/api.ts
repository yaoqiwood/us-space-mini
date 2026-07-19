const API_BASE_URL = "http://127.0.0.1:8000/v1";

export function request<T>(
  path: string,
  method: WechatMiniprogram.RequestOption["method"] = "GET",
  data?: Record<string, unknown>,
): Promise<T> {
  return new Promise((resolve, reject) => {
    wx.request<T>({
      url: `${API_BASE_URL}${path}`,
      method,
      data,
      success: (response) => {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data);
          return;
        }
        reject(new Error(`Request failed with status ${response.statusCode}`));
      },
      fail: reject,
    });
  });
}
