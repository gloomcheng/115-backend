# Editorial Review Report: 06 資源建模與 REST

## 1. 核心概念原子性檢驗

- [x] 單一核心命題：`path` 只命名資源，`method` 表達動作；換掉 Request Line 的第一個字，Server 的動作與回來的 Status Code 就一起換掉。
- [x] 沒有重講第一單元的安全 / 冪等定義，只在第 05 節引用並現場驗證。
- [x] 段落推進單一因果鏈：讀一次 → 建一次 → 為什麼不能 `GET` → 路由比對 → `201` 沒替我做的事 → 重送兩次 → 終端機驗證。

## 2. 先備知識與認知盲區

| 出現術語 / 概念 | 讀者是否已知 | 處理手段 |
| --- | --- | --- |
| collection / member | 否 | 第 01 節用一張集合—成員圖與實測結果表建立，兩個詞分別綁一個可觀察的 Status Code。 |
| REST | 第一單元提過「資源導向」一句 | 第 01 節直接給操作定義：path 回答「是哪一筆」，method 回答「做什麼」。 |
| 405 / `allow` | 否 | 第一次出現後緊接一段專門解釋 405 的語意，並要求學生記下 `allow` 這個 Header。 |
| Location | 否 | 第 04 節說明 RFC 對 `201` 的 SHOULD 與本機 API 未實作的後果。 |
| idempotent | 第一單元提過 | 第 05 節補上「重送一次不會得到同樣的最終結果」這個白話定義，再用兩次 `POST` 驗證覆蓋行為。 |
| 爬蟲與 prefetch 觸發 GET | 否 | 第 02 節以「自動行為不等於你的意圖」說明，並指出測試不會發現這類 bug。 |

## 3. 可驗證性與視覺圖解

- [x] 所有結論都在本機 `examples/http-api` 上重跑過，沒有依賴 httpbin 的不確定輸出。
- [x] 配備三張 ELI5 向量圖：三種 method 的 Status Line 對照、集合與成員、路由比對的三個出口。
- [x] `405`、`allow`、`404 User not found`、`POST` 覆蓋皆有 Terminal 可執行指令與實際輸出。

## 4. 兩段閱讀視窗稽核

- [x] `node scripts/reading-window-harness.mjs`：23 個相鄰視窗全數通過，0 個 window finding，0 個 concept finding。
- [x] 銜接點是實質的因果橋：「那個會被自動觸發的 GET」、「三次讀取與兩次建立的差別看過了」、「讀取不改狀態，上一步那三行輸出就是證據」。
- [x] harness 已加入 week 6 的 concept contracts（REST / 405 / Location / idempotent）。

## 5. 多角色審查

### 20 歲零基礎學生

- `GET /users/delete?id=bob` 回 `404 User not found` 這一個例子，把「動作不要寫進網址」講成看得見的事，不用記規則。
- 第五節的 `POST` 覆蓋實驗讓「POST 沒有冪等性」變成兩行輸出，不靠背。
- 作業有明確截圖清單，每張都指定要看見哪一行。

### 技術架構師

- 路由比對說明符合 RFC 9110 §9 與 Starlette 的 partial match 行為，並區分 `404`（沒有這個目標）與 `405`（有路徑、沒 method）。
- `201` 缺少 `Location` 的描述準確對應 SHOULD 而非 MUST，也沒有誤稱框架漏做。
- RFC 引用的 anchor 全部實際驗證存在於 rfc-editor 的 HTML。

### 主編

- 承接第二單元的 path / query / Body 分工，沒重複第二單元的內容。
- 沒有導入 ORM、HTTP/2 或版本化這些尚未排定的概念。
- 第 06 節把全文結論收成四組可截圖的對照，節奏乾淨。

## 6. 編輯綜合評定

- **讀者可讀性等級**：A
- **技術嚴謹度**：A
- **修改行動清單**：持續執行 `npm run check` 確認全部 gates 通過。