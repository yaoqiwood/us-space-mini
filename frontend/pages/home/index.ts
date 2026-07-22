import { checkApiHealth } from "../../utils/api";
import { clearSession, getCurrentUser } from "../../utils/session";

Page({
  data: {
    displayName: "",
    loading: true,
    errorMessage: "",
    backendStatus: "checking",
    backendMessage: "正在连接后端服务",
    quickActions: [
      { key: "todos", asset: "todo.png", label: "待办清单" },
      { key: "wishes", asset: "wish.png", label: "愿望清单" },
      { key: "anniversary", asset: "anniversary.png", label: "纪念日" },
      { key: "meal", asset: "meal.png", label: "今天吃什么" },
      { key: "checkin", asset: "checkin.png", label: "一键报备" },
      { key: "journal", asset: "journal.png", label: "日常记录" },
    ],
    todayPlans: [
      { title: "一起吃早餐", emoji: "🍞", time: "08:30" },
      { title: "一起去图书馆", emoji: "📚", time: "14:00" },
      { title: "晚上一起散步", emoji: "🌿", time: "20:00" },
    ],
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

  onQuickAction(event: WechatMiniprogram.BaseEvent) {
    const key = event.currentTarget.dataset.key as string;
    if (key === "checkin") {
      this.openNotificationSettings();
      return;
    }
    wx.showToast({ title: "功能正在准备中", icon: "none" });
  },

  onAddPlan() {
    wx.showToast({ title: "待办功能即将开放", icon: "none" });
  },

  onTabTap(event: WechatMiniprogram.BaseEvent) {
    if (event.currentTarget.dataset.tab !== "home") {
      wx.showToast({ title: "功能正在准备中", icon: "none" });
    }
  },

  onLogout() {
    clearSession();
    wx.reLaunch({ url: "/pages/login/index" });
  },
});
