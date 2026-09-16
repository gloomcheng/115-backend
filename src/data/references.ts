/**
 * Course reference data.
 * Each entry is a citable external resource that informed course design,
 * curriculum structure, or lesson content. Copy only; no layout logic here.
 *
 * category values:
 *   - 'textbook'     — published book or monograph
 *   - 'course'       — open university or institutional course material
 *   - 'spec'         — standards body specification
 *   - 'codelab'      — interactive lab or tutorial
 *   - 'talk'         — recorded conference talk or lecture
 */

export type ReferenceCategory = 'textbook' | 'course' | 'spec' | 'codelab' | 'talk'

export interface ReferenceEntry {
  id: string
  title: string
  author: string
  affiliation?: string
  url: string
  category: ReferenceCategory
  /** Free-form note explaining how it connects to this course */
  note: string
  /** Lesson weeks that directly draw on this reference */
  relatedWeeks?: number[]
  /** CC or publisher licence string, if known */
  license?: string
}

export const referencesData = {
  page: {
    title: '參考資料',
    kicker: 'REFERENCES',
    reader: 'COURSE BIBLIOGRAPHY',
    description: '本課程設計、課綱架構與講義撰寫時參照的外部資源，依類別列出並標示相關單元。',
    categoryLabels: {
      course: '課程教材',
      textbook: '教科書',
      spec: '規格文件',
      codelab: '實作教程',
      talk: '演講',
    } satisfies Record<ReferenceCategory, string>,
    categoryOrder: ['course', 'textbook', 'spec', 'codelab', 'talk'] satisfies ReferenceCategory[],
    relatedWeeksPrefix: '相關單元：第 ',
    relatedWeeksSuffix: ' 週',
    relatedWeeksSep: '、',
    licenseLabel: '授權',
  },
  entries: [
    {
      id: 'ccc-taobao-arch',
      title: '向淘寶學習網站架構演進',
      author: '陳鍾誠',
      affiliation: '國立金門大學 資訊工程系',
      url: 'https://github.com/ccc115a/se/tree/main/_more/mybook/%E5%90%91%E6%B7%98%E5%AF%B6%E5%AD%B8%E7%BF%92%E7%B6%B2%E7%AB%99%E6%9E%B6%E6%A7%8B%E6%BC%94%E9%80%B2',
      category: 'course',
      note: '以「問題驅動」方式重現從 100 併發到千萬級的 14 次架構演進，示範從單體、快取、負載均衡、資料庫分片，到 Docker / Kubernetes 的教學敘事結構。本課程後半學期討論 VPS 部署與服務化時，借鑑其「先製造運維痛點、再引入工具」的講義設計手法，避免純介紹工具清單。',
      relatedWeeks: [14, 15, 16, 17],
      license: 'MIT',
    },
    {
      id: 'rfc9110',
      title: 'HTTP Semantics (RFC 9110)',
      author: 'R. Fielding, M. Nottingham, J. Reschke',
      affiliation: 'IETF',
      url: 'https://www.rfc-editor.org/rfc/rfc9110',
      category: 'spec',
      note: '現行 HTTP/1.1 語意規範。課程對 Method 冪等性、Status Code 分類與 Header 欄位責任的描述均依 RFC 9110 為準，所有工程判斷聲明皆可追溯至此文件。',
      relatedWeeks: [1, 2, 3, 4],
    },
    {
      id: 'rfc3986',
      title: 'Uniform Resource Identifier (URI): Generic Syntax (RFC 3986)',
      author: 'T. Berners-Lee, R. Fielding, L. Masinter',
      affiliation: 'IETF',
      url: 'https://www.rfc-editor.org/rfc/rfc3986',
      category: 'spec',
      note: 'URI 通用語法規範，定義了 scheme、authority、path、query 與 fragment 的正式文法。課程第 2 單元 URL 拆解與 Fragment 不送給 Server 的論述均源自此規範。',
      relatedWeeks: [2],
    },
    {
      id: 'rfc2324',
      title: "Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0) — 418 I'm a teapot (RFC 2324)",
      author: 'L. Masinter',
      affiliation: 'IETF',
      url: 'https://www.rfc-editor.org/rfc/rfc2324',
      category: 'spec',
      note: "1998 年愚人節 RFC，定義了 418 I'm a teapot。課程以此示範「已部署行為會反過來影響規格」——RFC 9110 後來保留 418 為 Unused 而非重新分配，即是其後果。",
      relatedWeeks: [1],
    },
  ] satisfies ReferenceEntry[],
}
