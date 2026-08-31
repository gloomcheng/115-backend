# Editorial Review Report: 17 把 VPS 變成公開服務

## 1. 核心概念原子性檢驗

- [x] 單一核心命題：外部 Request 如何從網域通過 VPS 的公開入口，到達只在本機開放的 FastAPI。
- [x] Docker、Nginx、DNS、firewall 與 TLS 都只解釋這條 Request path 中的責任。
- [x] 未展開 load balancing、Kubernetes、多機容災與資料庫備份。

## 2. 先備知識與認知盲區

| 出現術語 / 概念 | 讀者是否已知 | 處理手段 |
| --- | --- | --- |
| Server | 否 | 第一節先建立「等 Request、回 Response 的程式」，不把 Server 當成特殊機器 |
| VPS | 否 | 定義為放在網路上、可長時間運作的遠端 Linux 電腦 |
| `127.0.0.1` | 不一定 | 在內外部連線對比前，先建立「當前這台電腦」的最小事實 |
| DNS `A` record | 否 | 放進 Request path，並用 `dig` 驗證回傳值 |
| TCP port / firewall | 否 | 只介紹 `22`、`80`、`443`、`8000` 與這次部署的責任 |
| Reverse proxy | 否 | 先畫 Request path，再引入 Nginx 術語與 `proxy_pass` |
| TLS termination | 否 | 在 HTTP 已可驗證後再引入，不提前展開密碼學 |
| `X-Forwarded-*` | 否 | 只解釋 Nginx 與 FastAPI 之間原始連線資訊的傳遞 |
| Test / harness | 不一定 | 先完成第一次公開 HTTPS `200`，再把手動 proof 轉成自動門禁 |
| Secret rotation | 否 | 用 warning 明確指出外洩後第一步是 revoke / rotate，不是只刪檔 |
| 備份、HA、零停機 | 否 | Callout 錨定為本單元邊界，不干擾主線 |

## 3. 可驗證性與視覺圖解

- [x] 一張與 repo 同風格的 ELI5 Request path 圖，只證明 Nginx 是唯一公開入口。
- [x] 每一關都有對應 proof：`dig`、`ssh`、`ufw`、`ss`、`docker compose ps`、`nginx -t`、`curl -v` 與 `certbot renew --dry-run`。
- [x] API 成功 / 失敗路徑有 pytest；secret policy 本身也有 Node test，不是只寫一支未驗證的 scanner。
- [x] Pre-commit、CI 與 live deployment 各有可執行 gate，並且失敗時回傳非零 exit status。
- [x] 先驗證內部 `200`，再驗證公開 `8000` 連線失敗，最後驗證 Nginx 的公開 HTTPS `200`。
- [x] 從 Terminal 穿透到 Browser：最後以 `/docs` 頁面驗證 Response Body 如何變成 API 文件畫面。

## 4. 多角色審查

### 20 歲零基礎學生

- 命令明確分成「自己的電腦」與「VPS」，降低在錯誤主機執行的風險。
- 先用筆電上的 `curl` 與 FastAPI 建立 Client / Server 角色，再把同一關係搬到 VPS。
- 第一次公開 HTTPS `200` 完成前，不展開 CI、branch protection 與 secret manager。
- Test 先展示一個成功範例，再說明為什麼還要測 `404`。
- 範例 IP 與網域有不可略過的替換提醒。
- 不要求讀者先背完 Linux 與 TLS，每一步只加一個可觀察證據。

### 技術架構師

- FastAPI 綁定 `127.0.0.1:8000`，只對外開放 Nginx 的 `80/443`。
- 明確指出 Docker published ports 可繞過 UFW，不把 UFW 當成唯一邊界。
- `X-Forwarded-*` 的信任條件與 `--forwarded-allow-ips=*` 的邊界一起出現。
- 憑證更新以 Certbot `dry-run` 驗證，不只驗證首次簽發。
- Secret 防線不只靠 `.gitignore`：包含 staged policy、Gitleaks、CI full-history scan、push protection 與外洩後 rotation 次序。

### 主編

- 開場直接使用「VPS 內 `200`、同事電腦連不到」的真實情境。
- 章節標題改為讀者當下要完成的判斷，不以 Docker、Nginx、Certbot 名詞切塊。
- 主線先完成公開 Request path，自動測試與 secret gate 放在成功後，不中斷第一次部署。
- 結尾停在實作交付條件，沒有再做一次摘要。

## 5. 編輯綜合評定

- **讀者可讀性等級**：A，專有名詞都在第一次影響操作前定義。
- **技術嚴謹度**：A，設定對齊 Ubuntu、Docker、NGINX、Certbot 與 FastAPI 官方文件。
- **修改行動清單**：草稿完成後執行 API tests、secret scanner tests、Gitleaks、deployment contract、MDX build、Docker Compose config、O'Reilly harness、CJK spacing 與瀏覽器桌面 / 行動寬度檢查。
