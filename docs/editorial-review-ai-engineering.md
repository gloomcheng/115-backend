# Editorial Review Report: AI 工程：讓模型能讀、能查、能被驗證

## 1. 核心概念原子性檢驗

- [x] 主線命題：AI 工程師要能追蹤資料從 token、向量、attention 到 tool、policy、test 的因果鏈。
- [x] 每個 Q 只回答一個「為什麼」，並用下一個 Q 建立依賴關係。
- [x] 沒有把 API 廠商功能清單當成模型原理。
- [x] 已把本單元接回 18 週 backend 課程：課程首頁、課程說明與作業規範都要求保留 AI 協作證據。

## 2. 先備知識與認知盲區

| 出現術語 / 概念 | 讀者是否已知 | 處理手段 |
| --- | --- | --- |
| Token | 否 | 先用 toy tokenizer 看文字變成序列 |
| Vector / Embedding | 否 | 先用整數 ID → embedding table 圖解，再區分 token embedding 與 text embedding |
| Position | 否 | 用相同 token 的兩種順序建立必要性 |
| Query / Key / Value | 否 | 用最小 QKᵀ → softmax → weighted values 流程圖與 toy scores |
| Multi-head | 否 | 以 syntax / reference 兩條關係路徑說明，不把 head 當成投票 |
| MLP | 否 | 明確區分資訊搬移與非線性特徵轉換 |
| MoE | 否 | 用 router 選少數 experts，補充負載平衡、記憶體與延遲代價 |
| Context window | 否 | 用有限工作區圖，連到 repository context 選擇 |
| RAG | 否 | 先建立文件 → chunk → retrieve → context → cite 的資料流 |
| Tool call / Policy gate | 否 | 以 model 是 Client、工具 Server 負責執行的責任邊界處理 |
| Eval | 否 | 固定 expected / actual，要求保留失敗案例與 trace |

## 3. 可驗證性與視覺圖解

- [x] 14 個 Q 各有一張原生 SVG ELI5 圖，每張只保留一條因果關係。
- [x] 每個 Q 都有可在 Terminal 執行的 toy proof；toy code 明確標示不等於正式模型實作。
- [x] Attention 題連結 3Blue1Brown 視覺化教材，影片後接矩陣問題，不把影片當成結論。
- [x] MoE 圖標出 active experts 與 total experts 的差異。
- [x] RAG 圖保留 retrieve 與 cite，沒有把 embedding 直接畫成答案。
- [x] Tool calling 與 Agent 權限圖將 model proposal 和 policy execution 分開。
- [x] 課程規則加入去識別化、AI 使用揭露、diff、測試與 log 的交付要求。

## 4. 多角色審查

### 20 歲零基礎學生

- 開場從「AI 改了四個檔案，誰證明它沒改壞」開始，先建立 coding agent 的責任問題。
- 每一題只新增一個必要機制，並在圖後留下能執行的最小觀察。
- 影片只放在 attention 題；學生仍要回答 QKᵀ、softmax 與 value 的資料流。

### 技術架構師

- 明確說明 self-attention 的平行化來自矩陣運算，不宣稱關聯數量變少；長度成本仍近似 `n²`。
- 明確區分訓練時的平行處理與 GPT 生成時的逐 token 解碼。
- MoE 的解釋包含 routing、active parameters、負載平衡、GPU communication 與記憶體代價。
- RAG、tool call 與 prompt 都沒有被當成 security boundary；授權留在模型外。

### 主編

- 章節順序是：表示 → 位置 → 關聯 → 轉換 → 條件計算 → 生成 → 外部記憶 → 外部行動 → 驗收與權限。
- 沒有用「AI 很強」「智慧地理解」等無法觀察的形容詞。
- 結尾停在 AI coding proof 的交付條件，沒有再做三段式總結。

## 5. 編輯綜合評定

- **讀者可讀性等級**：B+；概念依賴鏈完整，但單元密度高，下一輪應依實際課堂時間決定是否拆成兩單元。
- **技術嚴謹度**：A-；核心資料流與工程邊界清楚，正式模型 tokenizer、位置編碼與 MoE routing 尚未進入實作層。
- **視覺一致性**：A；使用既有課程的藍、黃、珊瑚色與原生 SVG，沒有新增外部圖片資產。
- **待驗收**：Astro dependency install、`astro check`、static build，以及 desktop / narrow viewport 的實際頁面觀察。
