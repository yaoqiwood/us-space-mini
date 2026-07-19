Page({
  data: {
    username: "",
    password: "",
    submitting: false,
  },

  onUsernameInput(event: WechatMiniprogram.Input) {
    this.setData({ username: event.detail.value });
  },

  onPasswordInput(event: WechatMiniprogram.Input) {
    this.setData({ password: event.detail.value });
  },

  onLogin() {
    wx.showToast({ title: "登录功能开发中", icon: "none" });
  },
});
