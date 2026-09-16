# Editorial Review Report: 01 HTTP 方法與狀態碼

## 1. 核心概念原子性檢驗

- [x] 單一核心命題：讀者能從 `curl -v` 的一去一回，辨認 Request、Response、Method、Status Code，以及 Client / Server 各自負責什麼。
- [x] 每個段落只推進一個判斷：封包結構 → 角色責任 → Method → Status Code → 瀏覽器畫面 → Terminal 驗證。
- [x] 移除超綱的 TCP 連線細節、session/Cookie/Token 堆疊、以及 402 中的 AI agent 付款協議，確保零基礎學生不產生認知超載。

## 2. 先備知識與認知盲區

| 出現術語 / 概念 | 讀者是否已知 | 處理手段 |
| --- | --- | --- |
| Request / Response | 否 | 開場先執行 `curl -v`，再用 `>` 與 `<` 對照真實輸出。 |
| path | 否 | 在第一週指明為目標路徑（例如 `/status/200`），不提前傾倒 scheme/port/query 術語包。 |
| reason phrase | 否 | 在第一次出現時說明它是狀態碼後的簡短文字，例如 `OK`。 |
| Header / Body | 不一定 | 說明 Header 為附加欄位資訊、空白行代表結束、Body 為承載訊息內容資料。 |
| stateless | 否 | 聚焦在「協定每次請求獨立、不自動儲存狀態」，認證憑證錨定於後續章節。 |
| resource | 否 | 在 Method 第一次出現時定義為 Server 上可識別的一筆資料或內容。 |
| 401 / 403 | 不一定 | 用「你是誰（認證）」與「能不能做（授權）」清楚切分，避免字面翻譯混淆。 |

## 3. 兩段閱讀視窗稽核

稽核對象是 `week: 1` 的 `src/content/lessons/01-http.mdx`。
相鄰段落驗證讀者能否在當下建立自然因果：上段提出操作或問題，下段承接其觀察結果或說明原因；消除為了湊關鍵字而機械拼接的 AI 膠水過渡句。

- [x] 開場指令與觀察結果緊密相扣：執行 `curl -v` 後立即聚焦於 `>` 與 `<` 的一去一回。
- [x] 封包結構說明直接對照 wire 實例，不作跨章節名詞空投。
- [x] Client / Server 切分奠基於「誰送出、誰決定」，並清楚說明程式在筆電上執行的角色。
- [x] Method 與 Status Code 形成自然的「動詞請求 → 結果回報」因果鏈。
- [x] 401 / 403 辨析與狀態碼總結自然帶出「純文字封包如何變成畫面」的核心疑問。
- [x] `node scripts/reading-window-harness.mjs --week 1`：30 個相鄰視窗全數通過，0 個 window finding，0 個 concept finding。

## 4. 可驗證性與視覺圖解

- [x] 讀者可執行 `curl -v https://httpbin.org/status/200`，直接看到 Request Line 與 Status Line。
- [x] `200`、`404`、`301` 的驗證指令沿用同一個 Request / Response 閱讀模型。
- [x] 四張 ELI5 圖各自只保留一條可觀察主張，並在正文中說明圖上的責任與方向。
- [x] `301` 的 `Location`、`404` 的 Status Code 與瀏覽器 Body 都接回可觀察輸出。

## 5. 多角色審查

### 20 歲零基礎學生

- 開頭直接動手打 `curl -v`，只要抓 `>` 和 `<`，沒有背誦術語的負擔。
- 每個新名詞都在第一次影響判斷的位置給予生活化定義，不堆砌未學名詞。
- 移除無關的 `.env` 虛擬環境要求，作業目標單純明確。

### 技術架構師

- Request Line、Status Line、Header、Body、Method、Status Code 的位置與語意完全符合 RFC 9110 / RFC 9112。
- `401` 與 `403` 依身份驗證與授權精確切分；`DELETE` 的冪等性依系統最終狀態判定。
- stateless 精確表達協定層無狀態，不與應用程式層混淆。

### 主編

- 節奏明快，刪除 AI 拼貼句與機械轉折，段落推進順暢。
- 單元原子性高，沒有延伸私貨干擾主線。
- 視角穿透清晰，成功把文字封包與瀏覽器繪製連結起來。

## 6. 編輯綜合評定

- **讀者可讀性等級**：A
- **技術嚴謹度**：A
- **修改行動清單**：持續維護 `reading-window-harness.mjs`，在提交前通過各項靜態檢查與 build 門禁。
