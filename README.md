# News Suite

## 项目简介

一个全流程系统，用于新闻抓取、AI 摘要/筛选、翻译、展示和订阅付费。

## 目录结构

```
news-suite/
├─ web/                         # Next.js 前端
├─ api/                         # FastAPI 后端
│  ├─ worker/                   # 爬虫、AI、翻译任务
│  ├─ shared/                   # 客户端与工具封装
├─ .env.example                 # 环境变量模板
├─ README.md                    # 项目说明
```

## 部署步骤

1. **克隆仓库**

   ```bash
   git clone <repository-url>
   cd news-suite
   ```

2. **配置环境变量**

   根据 `.env.example` 创建 `.env` 文件，并填写必要的值。

3. **安装依赖**

   后端：
   ```bash
   cd api
   pip install -r requirements.txt
   ```

   前端：
   ```bash
   cd web
   npm install
   ```

4. **运行项目**

   后端：
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

   前端：
   ```bash
   npm run dev
   ```

5. **部署到 Railway**

   - 推送到 GitHub
   - Railway 新建项目，分别部署 `web/` 和 `api/`。

## 验收清单

- [ ] 前端 `GET /api/health` 返回 `{ok:true}`
- [ ] 新建源站 → 定时任务能抓到文章
- [ ] 详情页能看到摘要/翻译
- [ ] 登录/注册工作正常；偏好可保存/读取
- [ ] 订阅：能从前端发起 Stripe Checkout；Webhook 正确更新订阅状态
