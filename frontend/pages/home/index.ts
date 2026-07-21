import { checkApiHealth } from "../../utils/api";
import { clearSession, getCurrentUser } from "../../utils/session";

Page({
  data: {
    displayName: "",
    loading: true,
    errorMessage: "",
    backendStatus: "checking",
    backendMessage: "正在连接后端服务",
  },

  onShow() {
    this.loadBackendHealth();
    this.loadCurrentUser();
  },

  async loadBackendHealth() {
    this.setData({ backendStatus: "checking", backendMessage: "正在连接后端服务" });
    try {
      const health = await checkApiHealth();
      this.setData({
        backendStatus: health.status === "ok" ? "online" : "error",
        backendMessage: health.status === "ok" ? "后端服务已连接" : "后端服务状态异常",
      });
    } catch (error) {
      this.setData({
        backendStatus: "error",
        backendMessage: `后端服务不可用：${(error as Error).message}`,
      });
    }
  },

  async loadCurrentUser() {
    this.setData({ loading: true, errorMessage: "" });
    try {
      const user = await getCurrentUser();
      this.setData({ displayName: user.display_name });
    } catch {
      clearSession();
      wx.reLaunch({ url: "/pages/login/index" });
    } finally {
      this.setData({ loading: false });
    }
  },

  openNotificationSettings() {
    wx.navigateTo({ url: "/pages/settings/notifications/index" });
  },

  onLogout() {
    clearSession();
    wx.reLaunch({ url: "/pages/login/index" });
  },
});
