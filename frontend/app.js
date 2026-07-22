App({
  globalData: {
    accessToken: "",
  },

  onLaunch() {
    this.globalData.accessToken = wx.getStorageSync("access_token") || "";
  },
});
