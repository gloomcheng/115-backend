# 網頁程式設計 — 115

第一週先用 `curl -v` 找出 Request Line 與 Status Line，再往後處理 REST、JSON、資料庫、認證與部署。每一段程式都要附一個能在 Terminal 重現的結果。

教材網站用 `npm run dev` 啟動。課堂使用的最小 FastAPI 放在 `examples/http-api`。

`RikaiDev/keiko` 是獨立開發的 backend agent harness。課程只會在它有可執行、可驗證的 release 後選用對應 proof，不以它取代 `curl` 或課堂 API。

## 怎麼上

```bash
npm install
npm run dev      # open http://localhost:4321
```

另外開一個 terminal 跑後端：

```bash
python3 -m venv venv && source venv/bin/activate
pip install "fastapi[standard]>=0.111.0"
fastapi dev examples/http-api/main.py
```

## 18 週

1. HTTP 方法與狀態碼 — 看懂 `curl -v`
2. URL / Header / Body 的長相
3. REST — 為什麼 `POST /users` 不是 `GET`
4. JSON — `422` 跟 `500` 不一樣
5. 後端怎麼接一個請求
6. 路由與 Handler
7. 寫第一個 `GET /health`
8. 存資料 — `File` 跟 `SQLite` 差在哪
9. 期中考試週
10. CRUD：新增、查詢、修改、刪除
11. 驗證與錯誤
12. 登入 — 身份認證與 `JWT`（`401` 跟 `403` 差在哪）
13. 中間件
14. 密鑰為什麼會外洩
15. 怎麼看 log
16. 用 Docker 包起來
17. 專題整合 — 串起 API、資料庫與部署
18. 期末考週（期末專題發表）

## 作業

Git 40% / 專題 60%。不要傳 `venv`、`__pycache__`、`.env`。

本教材由 Fuyuan Cheng 編寫，採 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hant) 授權。使用或改作時請標示作者與教材名稱。
