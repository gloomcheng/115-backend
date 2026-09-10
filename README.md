# 網頁程式設計 — 115

第一週先用 `curl -v` 找出 Request Line 與 Status Line，再往後處理 REST、JSON、資料庫、認證與部署。每一段程式都要附一個能在 Terminal 重現的結果。

## AI 協作與責任

你可以讓 AI 讀錯誤、解釋程式、整理文件或提出 patch。模型是在提出建議，不是在替你背責任。每次使用 AI，保留去識別化的上下文、diff、測試輸出與你自己的修改理由；`.env`、API key、Token 和個人資料不要貼進去。

完整說明請看[AI 工程指南](https://gloomcheng.github.io/115-backend/ai-engineering/)。規則參考[臺大生成式 AI 工具之教學因應措施](https://www.dlc.ntu.edu.tw/ai-tools/) 與 [數位發展部 AI 產業人才認定指引](https://moda.gov.tw/ADI/services/publications/19692)。

## backend 的職涯方向

這門課的職涯座標是資訊工程、資訊管理與雲端服務。你練的不是某個框架的按鈕，而是把請求、資料、權限、部署和證據接成一條可以交付的後端服務。

- **後端與 API 開發**：後端工程師、軟體設計工程師、系統分析師。
- **資料庫與資料工程**：資料庫管理人員、資料工程師、資料分析師。
- **資安與網路**：資安工程師、網路安全工程師、網路管理工程師。
- **雲端與系統維運**：雲端服務工程、系統維運、資安／網路管理、技術支援。
- **AI 應用與系統整合**：把 embedding、RAG、tool calling 和 eval 接回既有的 API、資料與權限邊界。

這些是能力可以連到的方向，不是保證的職稱。職稱會依公司和職務內容不同；先看你能負責哪一段，再去對照職缺。方向參考 [ColleGo! 資訊工程學類](https://collego.edu.tw/Highschool/MajorIntro?current_major_id=1)、[ColleGo! 資訊管理學類](https://collego.edu.tw/Highschool/MajorIntro?current_college_id=1&current_major_id=7)、[國發會雲端服務產業人力需求](https://theme.ndc.gov.tw/manpower/cp.aspx?n=C9ECDD0E995DB66B) 與 [數位發展部 AI 產業人才認定指引](https://moda.gov.tw/ADI/services/publications/19692)。

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
