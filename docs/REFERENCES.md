# 參考資料 — 網頁程式設計 115

> 每一堂的「為什麼這樣做」都有出處。

## HTTP

- **RFC 9110 HTTP Semantics** — 方法、狀態碼、Header 的唯一正本 <https://www.rfc-editor.org/rfc/rfc9110>
- **RFC 9112 HTTP/1.1** — 訊息怎麼在網路上切分 <https://www.rfc-editor.org/rfc/rfc9112>
- **MDN HTTP Overview** — 人話版總覽，適合先讀 <https://developer.mozilla.org/en-US/docs/Web/HTTP>
- **MDN Status / Methods** — 每個狀態碼與方法的白話解釋 <https://developer.mozilla.org/en-US/docs/Web/HTTP/Status> <https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods>

## URL / DNS / TLS

- **RFC 3986 URI** <https://www.rfc-editor.org/rfc/rfc3986>
- **RFC 8446 TLS 1.3** <https://www.rfc-editor.org/rfc/rfc8446>

## REST / JSON

- **RFC 9457 Problem Details for HTTP APIs** — 錯誤怎麼回才一致 <https://www.rfc-editor.org/rfc/rfc9457>
- **JSON Schema** <https://json-schema.org/>

## 應用框架

- **FastAPI Docs — HTTPException / Pydantic validation (422)** <https://fastapi.tiangolo.com/tutorial/handling-errors/> <https://docs.pydantic.dev/>
- **12 Factor App — Config** <https://12factor.net/config>

## 密碼學與密鑰管理

- **OWASP ASVS 4.0** — 驗證與存儲章節 <https://owasp.org/www-project-application-security-verification-standard/>
- **OWASP Top 10 A02 Cryptographic Failures** <https://owasp.org/Top10/A02_2021-Cryptographic_Failures/>
- **RFC 9106 Argon2** — 密碼雜湊 (為何用 Argon2id，不用 MD5/SHA256) <https://www.rfc-editor.org/rfc/rfc9106>
- **NIST SP 800-38D AES-GCM** — 加密 (為何用 GCM，不是 CBC) <https://csrc.nist.gov/publications/detail/sp/800-38d/final>

> `Argon2id` 用來雜湊密碼；`AES-GCM` 用來加密需要還原的資料。部署時，密鑰應由環境變數或密鑰管理服務提供，不應寫進程式碼、映像檔或資料庫欄位。

## 資料庫

- **SQLite WAL mode** <https://www.sqlite.org/wal.html>
- **Use The Index, Luke** — 為何查 10 萬筆會慢 <https://use-the-index-luke.com/>

## 部署

- **Dockerfile Best Practices** <https://docs.docker.com/develop/develop-images/dockerfile_best-practices/>
- **12 Factor — Port binding / Disposability** <https://12factor.net/port> <https://12factor.net/disposability>

## HTTP 冷知識與 Agent payment

- **RFC 2324 / RFC 9110 §15.5.19** — `418 I'm a teapot` 的來源，以及它為何被保留為 Unused <https://www.rfc-editor.org/rfc/rfc2324> <https://www.rfc-editor.org/rfc/rfc9110.html#name-418-unused>
- **Coinbase x402** — 以 `402 Payment Required` 建立每次 Request 的付款握手 <https://docs.cdp.coinbase.com/x402/how-it-works>
- **Google AP2** — 用可驗證 mandate 表達使用者交給 Agent 的付款授權 <https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol>
- **Stripe / OpenAI ACP** — Agent、商家與支付服務之間的 checkout 協定 <https://stripe.com/blog/developing-an-open-standard-for-agentic-commerce>

---

**怎麼用**：每堂投影片最後一頁只放 1 個出處，先讓學生點開看 5 分鐘，再回來寫 code。
