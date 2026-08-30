export interface WeekItem {
  w: number
  dates: string
  title: string
  href?: string
  exam?: boolean
  note?: string
}

export interface Chapter {
  num: string
  code: string
  title: string
  english: string
  range: string
  summary: string
  weeks: WeekItem[]
}

export const chapters: Chapter[] = [
  {
    num: '01',
    code: 'PROTOCOL',
    title: '網路原理與封包傳遞',
    english: 'Protocol & Wire Transmission',
    range: 'Week 01 – 07',
    summary: '從 HTTP 第一行 curl 開始，看懂 URL、Header、Body、REST 與狀態碼的真實結構。',
    weeks: [
      {
        w: 1,
        dates: '09/07–09/13',
        title: 'HTTP 方法與狀態碼 — 看懂 curl -v',
        href: '/lessons/01-http',
        note: '09/07 開學',
      },
      { w: 2, dates: '09/14–09/20', title: 'URL / Header / Body 的長相', note: '加退選截止' },
      {
        w: 3,
        dates: '09/21–09/27',
        title: 'REST — 為什麼 POST /users 不是 GET',
        note: '09/25 中秋放假',
      },
      { w: 4, dates: '09/28–10/04', title: 'JSON — 422 跟 500 不一樣', note: '09/28 教師節放假' },
      { w: 5, dates: '10/05–10/11', title: '後端怎麼接一個請求', note: '10/09 國慶補假' },
      { w: 6, dates: '10/12–10/18', title: '路由與 Handler' },
      { w: 7, dates: '10/19–10/25', title: '寫第一個 GET /health' },
    ],
  },
  {
    num: '02',
    code: 'PERSISTENCE',
    title: '關聯式資料庫與 ACID',
    english: 'Relational Model & SQLite Engine',
    range: 'Week 08 – 11',
    summary: '用 SQLite 練習交易與 CRUD，觀察一次寫入成功或回滾時，資料實際留下什麼。',
    weeks: [
      { w: 8, dates: '10/26–11/01', title: '存資料 — File 跟 SQLite 差在哪' },
      { w: 9, dates: '11/02–11/08', title: '期中考試週', exam: true, note: '期中考週' },
      { w: 10, dates: '11/09–11/15', title: 'CRUD：新增、查詢、修改、刪除' },
      { w: 11, dates: '11/16–11/22', title: '驗證與錯誤' },
    ],
  },
  {
    num: '03',
    code: 'CRUCIBLE',
    title: '資訊安全與身份認證',
    english: 'OWASP Top 10 & Auth Pipeline',
    range: 'Week 12 – 15',
    summary: '對齊 OWASP Top 10：JWT 認證、Argon2id 雜湊、AES-GCM 密鑰保護與 401/403 權限邊界。',
    weeks: [
      { w: 12, dates: '11/23–11/29', title: '登入 — 身份認證與 JWT（401 跟 403 差在哪）' },
      { w: 13, dates: '11/30–12/06', title: '中間件' },
      { w: 14, dates: '12/07–12/13', title: '密鑰為什麼會外洩' },
      { w: 15, dates: '12/14–12/20', title: '怎麼看 log' },
    ],
  },
  {
    num: '04',
    code: 'RUNTIME',
    title: '容器化與維運監控',
    english: 'Containers, Probes & Deployment',
    range: 'Week 16 – 18',
    summary: 'Docker 容器化標準：GET /health 探針、結構化 Log 分析與期末真實服務交付。',
    weeks: [
      { w: 16, dates: '12/21–12/27', title: '用 Docker 包起來', note: '12/25 行憲紀念日放假' },
      {
        w: 17,
        dates: '12/28–01/03',
        title: '專題整合 — 串起 API、資料庫與部署',
        note: '01/01 元旦放假',
      },
      {
        w: 18,
        dates: '01/04–01/10',
        title: '期末考週（期末專題發表）',
        exam: true,
        note: '學期考試週',
      },
    ],
  },
]
