# Editorial Review Report: 02 URI / URL、Header 與 Body

## 1. 核心概念原子性檢驗

- [x] 單一核心命題：將網址拆解為六個可觀察的零件，透過 `curl -v` 親眼驗證哪些資料進入了 HTTP Request 封包，哪些只留在 Client 端（如 `#fragment`）。
- [x] 每個段落推進明確判斷：網址實測 → URI / URL 概念 → 六大零件拆解 → Request Target 生成 → Header 與 Body 職責 → Path 與 Query 參數區分 → 終端機驗證。
- [x] 緊扣第一週建立的 `curl -v` 封包心智模型，沒有脫節。

## 2. 先備知識與認知盲區

| 出現術語 / 概念 | 讀者是否已知 | 處理手段 |
| --- | --- | --- |
| URI / URL | 不一定 | 說明 URI 是識別資源的總稱，URL 是提供定位地址的具體方式。 |
| scheme / host / port | 否 | 藉由 SVG 視覺圖解清楚對應實際字串，並說明 port 是主機上的網路入口。 |
| path / query | 第一週初見 | path 為資源路徑；query 為 `?` 後的參數，在傳輸層依舊是文字。 |
| fragment | 否 | 強調 `#` 後是瀏覽器內部定位用的標記，絕不會出現在送給伺服器的封包中。 |
| Header vs Body | 第一週初見 | 強化區分：Header 是附加 metadata，Body 是訊息內容本身；空白行是兩者的邊界。 |
| Path parameter vs Query parameter | 否 | 用極簡 FastAPI 範例對比 `/users/{name}` 與 `?active=true` 的語意差異。 |

## 3. 兩段閱讀視窗稽核

稽核對象是 `week: 2` 的 `src/content/lessons/02-url-headers-body.mdx`。
相鄰段落維持自然因果推進：先觀察指令與輸出差異，再推進語法拆解與伺服器接收狀態。

- [x] 開場貼入帶有 `#fragment` 的網址，直接觀察 `> GET` 中缺少 fragment 的現象。
- [x] 拆解六個零件的列表緊接前言，每一項均清楚交代 Client 與 Server 如何使用它。
- [x] Header 與 Body 的對比由具體的 GET（無 Body）與 POST（有 Body）封包並列呈現。
- [x] Path / Query parameter 的介紹直接連結到後端程式碼如何接收資料。
- [x] `node scripts/reading-window-harness.mjs --week 2`：17 個相鄰視窗全數通過，0 個 window finding，0 個 concept finding。

## 4. 可驗證性與視覺圖解

- [x] 讀者可執行 `curl -v 'https://httpbin.org/get?course=115&topic=uri#fragment'`，親眼看見 fragment 消失的物理事實。
- [x] 配備兩張 ELI5 向量圖（Request Target 與六大零件拆解），線條直接指向具體字元。
- [x] 提供包含 POST JSON 的終端機驗證指令，直接觀察 `Content-Type` 與 Body 的實體。

## 5. 多角色審查

### 20 歲零基礎學生

- 從瀏覽器天天看到的網址切入，把複雜的字串拆成 6 塊，有對照圖看得很清楚。
- 終於弄懂為什麼常常看到網址有 `?` 和 `&`，以及點擊網頁錨點跳轉時為什麼伺服器完全不知情。
- 作業只要圈出沒被送出的 fragment，目標明確。

### 技術架構師

- 符合 RFC 3986（URI 語法）與 RFC 9110（HTTP 語意）。
- 精確指出 fragment 留在 Client 端的規格原因，而非模糊帶過。
- 正確指出將機敏資料放在 URL query 會產生的 Log 洩漏風險，建立嚴謹的安全邊界。

### 主編

- 承接第一週的 Wire-view 視角，從「封包結構」平滑過渡到「網址如何變成封包」。
- 沒有使用廢話或 AI 式機械套話，直接給予技術判斷。
- 成功貫穿「從文字到程式」的視角，為後續的 FastAPI 實作打下堅實基礎。

## 6. 編輯綜合評定

- **讀者可讀性等級**：A
- **技術嚴謹度**：A
- **修改行動清單**：持續執行 `npm run check` 確認全部 gates 通過。
