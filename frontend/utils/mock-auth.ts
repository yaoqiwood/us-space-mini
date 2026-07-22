export interface MockUser {
  username: string;
  displayName: string;
}

const MOCK_ACCOUNTS: Record<string, { password: string; displayName: string }> = {
  mikyao1: { password: "123456", displayName: "MikYao" },
  mikyao2: { password: "123456", displayName: "星球" },
};

const MOCK_OPEN_ID = "mock-openid-development";
const MOCK_BINDINGS_KEY = "mock_openid_bindings";

function getBindings(): Record<string, string> {
  return wx.getStorageSync(MOCK_BINDINGS_KEY) || {};
}

function toMockUser(username: string): MockUser | null {
  const account = MOCK_ACCOUNTS[username];
  return account ? { username, displayName: account.displayName } : null;
}

export function getMockOpenId(): string {
  const openid = wx.getStorageSync("openid");
  if (typeof openid === "string" && openid.startsWith("mock-openid-")) {
    return openid;
  }
  wx.setStorageSync("openid", MOCK_OPEN_ID);
  return MOCK_OPEN_ID;
}

export function getMockBoundUser(openid: string): MockUser | null {
  return toMockUser(getBindings()[openid]);
}

export function loginWithMockAccount(
  username: string,
  password: string,
  openid: string,
): MockUser {
  const account = MOCK_ACCOUNTS[username];
  if (!account || account.password !== password) {
    throw new Error("账号或密码不正确");
  }

  const user = { username, displayName: account.displayName };
  const bindings = getBindings();
  bindings[openid] = username;
  wx.setStorageSync(MOCK_BINDINGS_KEY, bindings);
  wx.setStorageSync("mock_session", user);
  wx.setStorageSync("access_token", `mock-token-${username}`);
  getApp<{ globalData: { accessToken: string } }>().globalData.accessToken = `mock-token-${username}`;
  return user;
}
