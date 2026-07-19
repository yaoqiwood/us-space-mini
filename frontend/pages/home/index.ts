import { clearSession, getCurrentUser } from "../../utils/session";

Page({
  data: {
    displayName: "",
    loading: true,
    errorMessage: "",
  },

  onShow() {
    this.loadCurrentUser();
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
