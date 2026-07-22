import { ApiError, request } from "./api";

export interface AuthenticatedSession {
  status: "authenticated";
  access_token: string;
  refresh_token: string;
  openid: string;
  token_type: "bearer";
}

export interface BindingRequired {
  status: "binding_required";
  binding_token: string;
  openid: string;
}

export type WeChatLoginResult = AuthenticatedSession | BindingRequired;

export interface CurrentUser {
  id: string;
  username: string;
  display_name: string;
}

type CoupleSpaceApp = {
  globalData: {
    accessToken: string;
  };
};

function getLoginCode(): Promise<string> {
  return new Promise((resolve, reject) => {
    wx.login({
      success: (result) => {
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

function saveSession(session: AuthenticatedSession): void {
  wx.setStorageSync("access_token", session.access_token);
  wx.setStorageSync("refresh_token", session.refresh_token);
  getApp<CoupleSpaceApp>().globalData.accessToken = session.access_token;
}

export function saveOpenId(openid: string): void {
  wx.setStorageSync("openid", openid);
}

export function getStoredOpenId(): string {
  return wx.getStorageSync("openid") || "";
}

export function clearSession(): void {
  wx.removeStorageSync("access_token");
  wx.removeStorageSync("refresh_token");
  getApp<CoupleSpaceApp>().globalData.accessToken = "";
}

export async function loginWithWeChat(): Promise<WeChatLoginResult> {
  const code = await getLoginCode();
  const result = await request<WeChatLoginResult>("/auth/wechat", {
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

export async function bindCurrentWeChatAccount(
  username: string,
  password: string,
  bindingToken: string,
): Promise<void> {
  const session = await request<AuthenticatedSession>("/auth/bind", {
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

export async function refreshSession(): Promise<boolean> {
  const refreshToken = wx.getStorageSync("refresh_token");
  if (!refreshToken) {
    return false;
  }
  try {
    const session = await request<AuthenticatedSession>("/auth/refresh", {
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

export async function getCurrentUser(): Promise<CurrentUser> {
  try {
    return await request<CurrentUser>("/auth/me");
  } catch (error) {
    if (!(error instanceof ApiError) || error.statusCode !== 401 || !(await refreshSession())) {
      throw error;
    }
    return request<CurrentUser>("/auth/me");
  }
}
