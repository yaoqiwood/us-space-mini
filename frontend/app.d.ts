export {};

declare global {
  interface IAppOption {
    globalData: {
      accessToken: string;
    };
  }
}
