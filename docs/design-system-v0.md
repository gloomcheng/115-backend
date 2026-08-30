# 115 Backend Design System v0 — 討論稿

## 0. 這份系統解決什麼

這是技術課程網站，不是產品 landing page，也不是雜誌封面。

讀者第一次進來要完成三件事：找到正在上的課、看懂這週要驗證的問題、回到整學期的位置。設計系統只服務這三件事。

**固定內容：** 現有課名、標題、段落、按鈕、週次、日期、評量資訊不改。

**可變內容：** 位置、格線、字重、色彩角色、分隔方式、元件表現、行動裝置轉換。

## 1. 研究結論

Web Grand Prix 2018–2025 的 134 個官方得獎網站不是同一種「日本風格」：機場、企業、教育、文化、推廣與無障礙網站使用不同資訊結構。可重複的做法是讓版面服從使用者任務，例如找航班、理解品牌、閱讀知識或完成申請。

因此本系統不用「日式」「佗寂」「高級」當指令。每一個頁面使用明確的 route contract。

公開的 UI skill 也把 design system 和畫面 prompt 分開：先定 design token 與元件角色，再描述該頁的 Header、主要內容、行動與手機轉換。這份文件遵循同一層次。

## 2. 視覺 token

| Role | Token | Value | 用途 |
| --- | --- | --- | --- |
| Page surface | `surface-base` | `#F4F1EA` | 全頁底色 |
| Raised evidence | `surface-evidence` | `#FFFCF6` | Terminal、原始 HTTP、目前週次 |
| Primary ink | `text-primary` | `#1D1C19` | 標題、正文、關鍵操作 |
| Secondary ink | `text-secondary` | `#68655D` | 說明、日期、輔助資訊 |
| Structural rule | `border-subtle` | `#D1CCC1` | 路徑、列表、分節 |
| Anchor point | `anchor-red` | `#B94332` | 每個首屏唯一的閱讀座標 |

這是色彩**角色**，不是每個頁面都必須出現的調色盤。頁面首屏只可有一個 `anchor-red`：6 px（mobile）或 8 px（desktop）的實心圓。它固定標出「你現在位於這條路徑的哪裡」，不拿來上色按鈕、標籤、日期、rule 或大標。所有操作與狀態改由位置、字重、底線與文字說明區分。

## 3. 字體與數字

| Role | Font | Weight | Size / leading |
| --- | --- | --- | --- |
| Display | Noto Sans TC | 700–900 | 40–72 px / 1.06 |
| Section title | Noto Sans TC | 700 | 28–40 px / 1.2 |
| Reading | Noto Sans TC | 400–500 | 17–19 px / 1.85 |
| Metadata | JetBrains Mono | 400–500 | 11–13 px / 1.45 |
| Wire/code | JetBrains Mono | 400–700 | 13–16 px / 1.65 |

不用明體，不用手寫字，不用「日式」字體來充當風格。大標只在頁面真正的主要問題出現一次；其餘層級以尺寸、空間和規則處理。

## 4. 版面幾何

| Breakpoint | Frame | Grid | Gutter | Side margin |
| --- | --- | --- | --- | --- |
| Desktop ≥ 1280 | 1440 px max | 12 columns | 24 px | 48 px |
| Tablet 768–1279 | full width | 8 columns | 20 px | 32 px |
| Mobile < 768 | full width | 4 columns | 16 px | 16 px |

- 垂直間距只用 12、24、48、96 px 四個階級。
- 規則是結構，不是裝飾：章節、清單、證據區才可用 1 px rule。
- 不用陰影堆疊；surface 區隔順序固定為：空白 → 對齊 → rule → 淡色面 → border。

## 5. Route contracts

### A. 課程首頁

- Hero 保留現有標題、說明與三個入口；在課程定位行放一個唯一的 red anchor。
- Desktop 以 8/4 欄分配：左邊是課程說明；右邊只放目前週次與其 Request/Response 證據。
- 四個章節不是等寬 cards，而是垂直 route：每組左側為章節定位，右側為週次清單。
- 手機依序為課程說明 → 本週 → 章節路徑；日期和週碼不可隱藏。

### B. 單元講義／整冊閱讀

- Desktop 的正文為 8 欄；保留 3 欄做 marginal navigation 或章節定位，不擺廣告式側卡。
- 每個 H2 是一次理解轉換：命題 → 證據圖 → command → 結論。
- Diagram 緊接它要證明的句子，不能用作 section banner。
- Code 與 raw HTTP 可以跨滿正文欄；不能在手機水平裁切。

### C. 前置準備／詞彙字典

- 以 4/8 欄的 label/content 對照呈現。
- 連續 list + rule，不是每一筆都有獨立白卡。
- 導覽可 sticky，但不能壓縮正文或替代正文 heading。

## 6. 元件

| Component | 必要規則 |
| --- | --- |
| Header | 一條低對比底線；品牌左、主要導航右；手機換成兩列，不用漢堡選單。 |
| Anchor dot | 首屏唯一 6–8 px 實心紅點，緊鄰頁面定位資訊；不可複製成 badge 或清單符號。 |
| Current lesson | 唯一可填色 surface；顯示原本的 title、日期與 raw HTTP，但不用紅色。 |
| Chapter route | 左欄顯示章節定位；右欄週次依 rule 串接；只有可進入週次顯示動作。 |
| Code block | 深墨 surface；copy 操作在右上；不使用圓角或卡片陰影。 |
| Callout | 左側細線＋標籤；不用整塊彩色通知框。 |
| Diagram | 原生 SVG/HTML；Client/Server 必須是可辨識的描線物件；文字只放命題所需的 evidence label。 |

## 7. 明確禁止

- 改寫既有文案來配合版面。
- 用文化、年代或材質形容詞代替 layout 規格。
- 把紅色當成 CTA、hover、章節編號、日期、badge 或多個裝飾點。
- 所有區塊都使用 card、border、shadow 或相同 padding。
- Hero 插畫、假紙張紋理、破紙、手寫字、裝飾性 logo。
- Diagram 放 Unit、標題、口號、頁尾或不指向畫面證據的文字。
- 以 hover 才能看見重要資訊。

## 8. 驗收

1. Desktop 1440 px：第一眼依序看到課程標題、本週、可進入的下一步。
2. Mobile 390 px：不裁切標題、日期、code 或 diagram；導航仍可讀。
3. 原本文案 diff 為零。
4. `node scripts/curatorial-harness.mjs`、`astro check`、`astro build` 必須通過。
5. 每次 layout 改動以實際頁面 screenshot 評閱，不以 source code 判定好壞。

## 9. 需要確認的決策

- 同意以無襯線 Noto Sans TC 作為 display/reading font？
- 同意首頁採 8/4 hero + 垂直 chapter route，而不是四張卡？
- 同意每個首屏只用一個 red anchor，其他層級完全以黑、灰、rule 與 surface 處理？
- 同意 diagrams 一律優先原生 SVG/HTML，而不是生成式插圖？
