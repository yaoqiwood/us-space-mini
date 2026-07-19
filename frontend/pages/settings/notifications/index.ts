import { subscriptionTemplates } from "../../../config";
import { request } from "../../../utils/api";

type TemplateKey = "check_in" | "meal_request";

Page({
  data: {
    statusMessage: "",
  },

  async requestSubscription(event: WechatMiniprogram.BaseEvent) {
    const templateKey = event.currentTarget.dataset.templateKey as TemplateKey;
    const templateId = templateKey === "check_in"
      ? subscriptionTemplates.checkIn
      : subscriptionTemplates.mealRequest;
    if (!templateId) {
      this.setData({ statusMessage: "订阅模板尚未配置" });
      return;
    }

    try {
      const result = await new Promise<Record<string, string>>((resolve, reject) => {
        wx.requestSubscribeMessage({ tmplIds: [templateId], success: resolve, fail: reject });
      });
      const subscriptionStatus = result[templateId] === "accept" ? "accept" : "reject";
      await request(`/notifications/subscriptions/${templateKey}`, "PUT", { status: subscriptionStatus });
      this.setData({ statusMessage: subscriptionStatus === "accept" ? "已开启通知" : "未开启通知" });
    } catch {
      this.setData({ statusMessage: "无法请求通知授权" });
    }
  },
});
