const { ApiError, request } = require("./api");

function getLoginCode() {
  return new Promise((resolve, reject) => {
    wx.login({
      success(result) {
        if (result.code) {
          resolve(result.code);
          return;
        }
        reject(new Error("WeChat did not return a login code"));
      },
      fail: reject,
    });
  });
}

function saveSession(session) {
  wx.setStorageSync("access_token", session.access_token);
  wx.setStorageSync("refresh_token", session.refresh_token);
  getApp().globalData.accessToken = session.access_token;
}

function saveOpenId(openid) {
  wx.setStorageSync("openid", openid);
}

function getStoredOpenId() {
  return wx.getStorageSync("openid") || "";
}

function clearSession() {
  wx.removeStorageSync("access_token");
  wx.removeStorageSync("refresh_token");
  getApp().globalData.accessToken = "";
}

async function loginWithWeChat() {
  const code = await getLoginCode();
  const result = await request("/auth/wechat", {
    method: "POST",
    data: { code },
    authenticated: false,
  });
  saveOpenId(result.openid);
  if (result.status === "authenticated") {
    saveSession(result);
  }
  return result;
}

async function bindCurrentWeChatAccount(username, password, bindingToken) {
  const session = await request("/auth/bind", {
    method: "POST",
    data: {
      username,
      password,
      binding_token: bindingToken,
    },
    authenticated: false,
  });
  saveSession(session);
}

async function refreshSession() {
  const refreshToken = wx.getStorageSync("refresh_token");
  if (!refreshToken) {
    return false;
  }
  try {
    const session = await request("/auth/refresh", {
      method: "POST",
      data: { refresh_token: refreshToken },
      authenticated: false,
    });
    saveSession(session);
    return true;
  } catch {
    clearSession();
    return false;
  }
}

async function getCurrentUser() {
  try {
    return await request("/auth/me");
  } catch (error) {
    if (!(error instanceof ApiError) || error.statusCode !== 401 || !(await refreshSession())) {
      throw error;
    }
    return request("/auth/me");
  }
}

module.exports = {
  bindCurrentWeChatAccount,
  clearSession,
  getStoredOpenId,
  getCurrentUser,
  loginWithWeChat,
  saveOpenId,
};
