# Git history 實驗

這個 lab 先用 `v1 / v2 / v3` 資料夾重現問題，再用 commit graph 取代檔名猜測。

依〈Git：不要再存 project-v3-final〉完成實驗後執行：

```bash
node "$COURSE_ROOT/exercises/git-history/check.mjs" "$GIT_LAB"
```

Checker 會實際讀取 Git objects 與 references，驗證：

- `0.9` snippet 在 history 中可追查，而且最後已取回。
- shipping rebase 前後 commit ID 不同。
- shipping 與 hotfix 已進入 `main`。
- conflict resolution 是有兩個 parent 的 merge commit。
- 解完的檔案沒有 conflict markers。
- 每個 worktree 都是 clean。

失敗時不要重來。先看：

```bash
git status
git diff
git diff --staged
git log --oneline --decorate --graph --all
```
