import { getMockBoundUser, getMockOpenId, loginWithMockAccount } from "../../utils/mock-auth";

Page({
  data: {
    username: "",
    password: "",
    submitting: false,
    hasEntered: false,
    checkingWeChat: false,
    needsAccountBinding: false,
    errorMessage: "",
    connectionMessage: "正在读取本地模拟身份...",
  },

  onEnter() {
    this.setData({ hasEntered: true });
    this.verifyMockIdentity();
  },

  onUsernameInput(event: WechatMiniprogram.Input) {
    this.setData({ username: event.detail.value });
  },

  onPasswordInput(event: WechatMiniprogram.Input) {
    this.setData({ password: event.detail.value });
  },

  verifyMockIdentity() {
    this.setData({
      checkingWeChat: true,
      errorMessage: "",
      needsAccountBinding: false,
      connectionMessage: "正在读取本地模拟身份...",
    });
    const openid = getMockOpenId();
    if (getMockBoundUser(openid)) {
      wx.reLaunch({ url: "/pages/home/index" });
      return;
    }
    this.setData({ needsAccountBinding: true, checkingWeChat: false });
  },

  onLogin() {
    if (!this.data.needsAccountBinding) {
      this.verifyMockIdentity();
      return;
    }
    this.setData({ submitting: true, errorMessage: "" });
    try {
      loginWithMockAccount(this.data.username, this.data.password, getMockOpenId());
      wx.reLaunch({ url: "/pages/home/index" });
    } catch (error) {
      this.setData({ errorMessage: (error as Error).message || "账号绑定失败" });
    } finally {
      this.setData({ submitting: false });
    }
  },
});
