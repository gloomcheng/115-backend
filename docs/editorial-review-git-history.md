# Editorial Review Report: Git 不要再存 project-v3-final

## 1. 核心概念原子性檢驗

- [x] 單一核心命題：資料夾副本只留結果，Git history 留下版本之間可查詢的變更關係。
- [x] Commit、branch、rebase、conflict 與 worktree 都用來回答「哪次改了什麼、從哪裡接著改、如何取回」。
- [x] 未展開 Git internals packing、server protocol、submodule 與 interactive rebase。

## 2. 先備知識與認知盲區

| 出現術語 / 概念 | 讀者是否已知 | 處理手段 |
| --- | --- | --- |
| Version | 只知道資料夾副本 | 先實際建立 v1 / v2 / v3，讓決策資料缺失可觀察 |
| Diff | 不一定 | 先用系統 `diff -u`，再轉到 Git patch |
| Commit | 不一定 | 在讀者已經提出四個歷史查詢需求後才命名 |
| RPG 記錄點 | 已知 | 只用於 commit 可取回性，立即補上 ID、parent、tracked / staged 邊界 |
| Branch / HEAD | 否 | 從兩份 v3 副本無法證明共同 base 推導 |
| Rebase | 否 | 用 rebase 前後真實 hash 證明 commit 被重建 |
| Conflict | 可能只看過 markers | 刻意建立同一行的兩個決策，再檢查 merge commit parents |
| Worktree | 否 | 從「真的需要兩個資料夾」的情境引入 |

## 3. 可驗證性與視角穿透

- [x] 讀者親手建立 copy-folder history，用 `diff` 與 `grep` 看到它能與不能回答的事。
- [x] `git log -S`、`git show <commit>:<path>` 與 `git restore --source` 完成 snippet 追查、閱讀與取回。
- [x] Rebase 以前後 hash 不等驗證，不只用線性圖口頭解釋。
- [x] Conflict 以一次必然失敗的 merge 驗證，再由 `git status` 指示下一步。
- [x] Checker 實際讀取 refs、commit ancestry、merge parents、file snapshots 與 worktree status。

## 4. 多角色審查

### 20 歲零基礎學生

- 開場先展示 `v1 / v2 / final / fix` 的真實命名行為，不要求讀者先接受 Git 術語體系。
- 每次只操作 `mktemp` 內的 lab，失敗不影響作業 repository。
- 具體回答「那段 snippet 怎麼找回來」，不只教 branch workflow。

### 技術架構師

- Branch 精確定義為 reference；HEAD、parent chain、working tree 與 index 邊界沒有被 RPG 比喻取代。
- Rebase 明確說明重建 commit ID，並禁止自行重寫已共享 history。
- Conflict resolution 不以 ours / theirs 快速蓋掉，要求先讀雙方決策。

### 主編

- 問題先於工具：資料夾副本的資訊缺口完整顯現後才引入 commit。
- RPG 比喻只出現在需要命名「可取回進度」的位置，沒有主導章節結構。
- 結尾停在 status / diff / graph 的操作前檢查，沒有再重述所有名詞。

## 5. 編輯綜合評定

- **讀者可讀性等級**：A，先解決熟悉行為引發的問題，再引入術語。
- **技術嚴謹度**：A，概念對齊 Git official manual 與 Pro Git。
- **待驗收**：MDX build、CJK spacing、Git lab replay、checker、desktop / mobile render。
