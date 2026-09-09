# 舊教材口吻與內容對照

更新日期：2026-09-09

這份筆記不是新的學生講義。它保存舊教材的來源、口吻特徵與目前 115-backend 的整合決定，讓下一次編輯可以先讀證據，不靠記憶仿寫。

## 來源

| 來源 | 保留到目前課程的內容 | 目前處理 |
| --- | --- | --- |
| [web-developer-course/ch1/Uniform_Resource_Locator.md](https://github.com/gloomcheng/web-developer-course/blob/master/ch1/Uniform_Resource_Locator.md)（commit `9556b22290ec04c8063e715ad13b24dc19b79f09`） | URL 的 `scheme`、`host`、`port`、`path`、`query`、`fragment` 拆解；用一個實際網址逐段說明 | 補進 Week 02；新增 URI / URL 的區分，修正把密碼放進 URL 與 fragment 傳送邊界的風險 |
| [web-dev-foundations/slides/http.md](https://github.com/gloomcheng/web-dev-foundations/blob/main/slides/http.md) | Request / Response 的原始文字、HTTP 方法、狀態碼與 `curl` 練習 | 保留 wire 範例；以 RFC 9110 / 9112 的精確語意取代「HTTP 每次都重新建立連線」等過度簡化 |
| [web-dev-foundations/slides/fastapi.md](https://github.com/gloomcheng/web-dev-foundations/blob/main/slides/fastapi.md) | 虛擬環境、最小 FastAPI、`/docs`、path / query / body / header | 前置準備與 Week 05–07、Week 11 的內容來源；目前 Week 02 只放路由對照，不提前展開框架驗證 |
| [fastapi-backend-course/README.md](https://github.com/gloomcheng/fastapi-backend-course/blob/main/README.md) | SQLAlchemy、Alembic、Pydantic、JWT、密碼雜湊的課程分層 | 對應 Week 08、11、12、14；未把套件清單塞進 HTTP 基礎課 |
| [114-backend/README.md](https://github.com/gloomcheng/114-backend/blob/main/README.md) | OAuth、環境變數、FastAPI `/docs` 與可執行安裝路徑 | 對應認證與密鑰章節；保留 `.env` 邊界與可觀察結果 |
| [docker-workshop/intro.md](https://github.com/gloomcheng/docker-workshop/blob/master/intro.md) | Docker 的 Why / How / What、先做再解釋、容器化與部署實作 | 對應 Week 16–17；不在 Week 02 提前加入容器命令 |

## 口吻特徵

1. 先從學生會做的動作開始：輸入網址、開 Terminal、啟動伺服器、看到錯誤。
2. 先給最小可執行路徑，再命名概念。命令不是裝飾；每條命令都要有可觀察的輸出。
3. 一段只做一個判斷。讀者要能指出哪一行輸出證明了結論。
4. 用直接句子下技術判斷，例如「這不是 bug，而是邊界的證據」；不把重要條件藏在委婉語氣裡。
5. 類比可以幫助定位角色，但不能取代封包、Status Line、Header、Body 或實際程式。
6. 先說責任邊界，再進入框架語法：誰送 Request、誰決定 Status Code、哪個程式讀取哪個欄位。
7. 結尾停在作業或驗收條件，不再用一段摘要重述整章。

## 115-backend 的一致性檢查

目前 `src/content/lessons/01-http.mdx` 已符合主要口吻：開頭直接使用 `curl -v`，先指出 `>` 與 `<`，再建立 Client / Server 的責任邊界；每個概念都接到終端指令、Status Line 或圖解。

新增的 Week 02 延續同一寫法：先用含有 `query` 與 `fragment` 的 URL，讓讀者在 Request Target 裡找證據，再補 URI / URL 名詞與組成表。舊教材的 URL 拆解被保留，但密碼不再作為可操作範例，`fragment` 明確標示為 Client 端處理。

目前仍不能把所有舊教材視為同一種文風。舊 `web-dev-foundations` 有較多郵差類比、emoji 與投影片式口號；舊 FastAPI 與 OAuth 文件偏向工具清單與步驟手冊。115-backend 應保留它們的實作順序與內容證據，刪掉不能幫助當前判斷的裝飾與框架清單。

## 知識庫 provenance

- 目前 innen 的 115-backend 證據節點：`source:8fd44807`。
- 來源標籤：`2026-09-02-codex-courses_115-backend.md`。
- 來源 SHA-256：`24872dccd73047f11be29906d2eee6533a6ff73b577a36078c6edff4e1c085c9`。
- 本次新增的內容先以本檔保存，再由 `innen artifact add` 登錄到 `/Users/gloomcheng/Workspace/innen-wiki`；沒有把私有 repository 或未取得的文件當成來源。
