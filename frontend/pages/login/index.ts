import { checkApiHealth } from "../../utils/api";
import { bindCurrentWeChatAccount, loginWithWeChat } from "../../utils/session";

Page({
  data: {
    username: "",
    password: "",
    submitting: false,
    checkingWeChat: true,
    bindingToken: "",
    errorMessage: "",
  },

  onLoad() {
    this.verifyBackendAndLogin();
  },

  onUsernameInput(event: WechatMiniprogram.Input) {
    this.setData({ username: event.detail.value });
  },

  onPasswordInput(event: WechatMiniprogram.Input) {
    this.setData({ password: event.detail.value });
  },

  async beginWeChatLogin() {
    this.setData({ checkingWeChat: true, errorMessage: "" });
    try {
      const result = await loginWithWeChat();
      if (result.status === "authenticated") {
        wx.reLaunch({ url: "/pages/home/index" });
        return;
      }
      this.setData({ bindingToken: result.binding_token });
    } catch (error) {
      this.setData({ errorMessage: (error as Error).message || "微信登录暂不可用" });
    } finally {
      this.setData({ checkingWeChat: false });
    }
  },

  async verifyBackendAndLogin() {
    this.setData({ checkingWeChat: true, errorMessage: "", bindingToken: "" });
    try {
      await checkApiHealth();
    } catch (error) {
      this.setData({ errorMessage: `无法连接后端服务：${(error as Error).message}` });
      this.setData({ checkingWeChat: false });
      return;
    }
    await this.beginWeChatLogin();
  },

  async onLogin() {
    if (!this.data.bindingToken) {
      this.verifyBackendAndLogin();
      return;
    }
    this.setData({ submitting: true, errorMessage: "" });
    try {
      await bindCurrentWeChatAccount(this.data.username, this.data.password, this.data.bindingToken);
      wx.reLaunch({ url: "/pages/home/index" });
    } catch (error) {
      this.setData({ errorMessage: (error as Error).message || "账号绑定失败" });
    } finally {
      this.setData({ submitting: false });
    }
  },
});
