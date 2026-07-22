const API_BASE_URL = "http://127.0.0.1:8000/v1";

class ApiError extends Error {
  constructor(statusCode, message, details) {
    super(message);
    this.name = "ApiError";
    this.statusCode = statusCode;
    this.details = details;
  }
}

function getErrorMessage(data, fallback) {
  if (typeof data === "string" && data) {
    return data;
  }
  if (!data || typeof data !== "object") {
    return fallback;
  }
  if (typeof data.detail === "string" && data.detail) {
    return data.detail;
  }
  return fallback;
}

function request(path, options = {}) {
  const {
    method = "GET",
    data,
    authenticated = true,
    timeout = 10000,
  } = options;
  const token = wx.getStorageSync("access_token");

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`,
      method,
      data,
      timeout,
      header: {
        "content-type": "application/json",
        ...(authenticated && token ? { Authorization: `Bearer ${token}` } : {}),
      },
      success(response) {
        if (response.statusCode >= 200 && response.statusCode < 300) {
          resolve(response.data);
          return;
        }
        reject(new ApiError(
          response.statusCode,
          getErrorMessage(response.data, `Request failed with status ${response.statusCode}`),
          response.data,
        ));
      },
      fail(error) {
        reject(new ApiError(0, error.errMsg || "Network request failed", error));
      },
    });
  });
}

function probeEntryService() {
  return request("/entry/probe", { authenticated: false });
}

module.exports = {
  ApiError,
  probeEntryService,
  request,
};
