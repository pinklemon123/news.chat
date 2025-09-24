const API_BASE = process.env.API_BASE!;
// 确保 API_BASE 环境变量存在
if (!API_BASE) {
  throw new Error("API_BASE 环境变量未定义");
}
export default {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${API_BASE}/:path*` }];
  },
};