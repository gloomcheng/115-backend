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
- **Docker Engine on Ubuntu** — 官方 apt repository、Compose plugin 與 UFW 注意事項 <https://docs.docker.com/engine/install/ubuntu/>
- **Docker Compose Ports** — 綁定 `127.0.0.1` 與公開 `0.0.0.0` 的差別 <https://docs.docker.com/reference/compose-file/services/#ports>
- **Ubuntu Server Firewall** — UFW 開放與查詢 port <https://documentation.ubuntu.com/server/how-to/security/firewalls/>
- **NGINX HTTP Proxy Module** — `proxy_pass` 與 `proxy_set_header` 的正式語意 <https://nginx.org/en/docs/http/ngx_http_proxy_module.html>
- **Certbot for Nginx** — 取得、安裝與測試自動更新 TLS 憑證 <https://certbot.eff.org/instructions?ws=nginx&os=snap>
- **FastAPI Behind a Proxy** — `X-Forwarded-*` Header 與受信任 proxy 邊界 <https://fastapi.tiangolo.com/advanced/behind-a-proxy/>
- **FastAPI Testing** — 使用 `TestClient` 與 pytest 驗證 Status Code 與 Response Body <https://fastapi.tiangolo.com/tutorial/testing/>
- **Gitleaks** — pre-commit 與 Git history 的 hardcoded secret 掃描 <https://github.com/gitleaks/gitleaks>
- **GitHub Push Protection** — 在 secret 到達 repository 前擋下 push <https://docs.github.com/en/code-security/concepts/secret-security/push-protection>
- **GitHub Sensitive Data Removal** — 先 revoke / rotate，再協調 Git history 處理 <https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository>
- **12 Factor — Port binding / Disposability** <https://12factor.net/port> <https://12factor.net/disposability>

## Git 版本管理

- **Pro Git — Recording Changes** — working tree、staging area、commit 與 diff <https://git-scm.com/book/en/v2/Git-Basics-Recording-Changes-to-the-Repository>
- **Git User Manual — What is a branch?** — branch reference、HEAD 與 parent history <https://git-scm.com/docs/user-manual#understanding-history>
- **Git Rebase** — 重播 commits、conflict 與 abort / continue <https://git-scm.com/docs/git-rebase>
- **Pro Git — The Perils of Rebasing** — 不重寫已共享 history 的邊界 <https://git-scm.com/book/en/v2/Git-Branching-Rebasing#_rebase_peril>
- **Git Worktree** — 一個 repository 同時管理多個 working trees <https://git-scm.com/docs/git-worktree>
- **Git Revert / Reflog** — 共享 commit 的反向修改與 local reference 移動記錄 <https://git-scm.com/docs/git-revert> <https://git-scm.com/docs/git-reflog>

## HTTP 冷知識與 Agent payment

- **RFC 2324 / RFC 9110 §15.5.19** — `418 I'm a teapot` 的來源，以及它為何被保留為 Unused <https://www.rfc-editor.org/rfc/rfc2324> <https://www.rfc-editor.org/rfc/rfc9110.html#name-418-unused>
- **Coinbase x402** — 以 `402 Payment Required` 建立每次 Request 的付款握手 <https://docs.cdp.coinbase.com/x402/how-it-works>
- **Google AP2** — 用可驗證 mandate 表達使用者交給 Agent 的付款授權 <https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol>
- **Stripe / OpenAI ACP** — Agent、商家與支付服務之間的 checkout 協定 <https://stripe.com/blog/developing-an-open-standard-for-agentic-commerce>

---

**怎麼用**：每堂投影片最後一頁只放 1 個出處，先讓學生點開看 5 分鐘，再回來寫 code。
