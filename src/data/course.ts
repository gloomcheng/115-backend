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
  aiFocus: string
  weeks: WeekItem[]
}

export const chapters: Chapter[] = [
  {
    num: '01',
    code: 'PROTOCOL',
    title: '網路原理與封包傳遞',
    english: 'Protocol & Wire Transmission',
    range: 'Week 01 – 04',
    summary:
      '先讀懂封包，再看後端怎麼接住請求：URL 的零件、請求的生命週期、路由表，以及你交付的第一段程式。',
    aiFocus: '模型可以提出 handler，但你要用 curl 讀出 Server 真正回了什麼。',
    weeks: [
      {
        w: 1,
        dates: '09/07–09/13',
        title: 'HTTP 方法與狀態碼 — 看懂 curl -v',
        href: '/lessons/01-http',
        note: '09/07 開學',
      },
      {
        w: 2,
        dates: '09/14–09/20',
        title: 'URI / URL / Header / Body 的長相',
        href: '/lessons/02-url-headers-body',
        note: '加退選截止',
      },
      {
        w: 3,
        dates: '09/21–09/27',
        title: '後端怎麼接一個請求 — 從封包到 Response 的五個階段',
        href: '/lessons/03-request-lifecycle',
        note: '09/25 中秋放假',
      },
      {
        w: 4,
        dates: '09/28–10/04',
        title: '路由與你的第一條程式 — path、method 與 /health',
        href: '/lessons/04-routing-and-first-endpoint',
        note: '09/28 教師節放假',
      },
    ],
  },
  {
    num: '02',
    code: 'DATA',
    title: '資料、介面與錯誤契約',
    english: 'Persistence, Interface & Error Contracts',
    range: 'Week 05 – 10',
    summary: '先讓資料活過行程結束，再把資源建模成路由，最後把驗證失敗變成可被程式讀懂的錯誤契約。',
    aiFocus: '模型可以提資料操作，但你要用測試確認資料沒有多一筆或少一筆。',
    weeks: [
      {
        w: 5,
        dates: '10/05–10/11',
        title: '存資料 — File 跟 SQLite 差在哪',
        href: '/lessons/05-persistence',
        note: '10/09 國慶補假',
      },
      {
        w: 6,
        dates: '10/12–10/18',
        title: '資源建模與 REST — 集合、成員與 201',
        href: '/lessons/06-resource-modeling',
      },
      {
        w: 7,
        dates: '10/19–10/25',
        title: 'JSON 與執行期驗證 — 422 是怎麼來的',
        href: '/lessons/07-json-validation',
      },
      {
        w: 8,
        dates: '10/26–11/01',
        title: 'CRUD — 四個 method 各自對資料庫做一次操作',
        href: '/lessons/08-crud',
      },
      { w: 9, dates: '11/02–11/08', title: '期中考試週', exam: true, note: '期中考週' },
      {
        w: 10,
        dates: '11/09–11/15',
        title: '驗證與錯誤 — 檢查寫在哪裡，決定 Client 拿到什麼',
        href: '/lessons/10-validation',
      },
    ],
  },
  {
    num: '03',
    code: 'CRUCIBLE',
    title: '資訊安全與身份認證',
    english: 'OWASP Top 10 & Auth Pipeline',
    range: 'Week 11 – 12',
    summary: '對齊 OWASP Top 10：JWT 認證、中介軟體的權限邊界，以及密鑰不外洩的規則。',
    aiFocus: '模型看不到密鑰，也不能替你決定誰有權限；認證與授權仍由 Server 負責。',
    weeks: [
      {
        w: 11,
        dates: '11/16–11/22',
        title: '登入 — 身份認證與 JWT',
        href: '/lessons/11-auth',
      },
      {
        w: 12,
        dates: '11/23–11/29',
        title: '中介軟體、權限與密鑰邊界',
        href: '/lessons/12-middleware',
      },
    ],
  },
  {
    num: '04',
    code: 'CONTRACT',
    title: '契約與對外介面',
    english: 'Contracts & External Interfaces',
    range: 'Week 13 – 14',
    summary:
      '先用測試把你自己的契約變成門禁，再讀別人的契約：SOAP、REST、GraphQL、gRPC、tRPC 怎麼表示型別與錯誤，以及為什麼 400 與 409 與 422 沒有標準答案。',
    aiFocus: '模型可以照抄一種錯誤格式；你要能指出對方的契約少了什麼。',
    weeks: [
      {
        w: 13,
        dates: '11/30–12/06',
        title: '測試 — 讓契約每次都被檢查',
        href: '/lessons/13-testing',
      },
      {
        w: 14,
        dates: '12/07–12/13',
        title: 'API 家族 — SOAP、REST、GraphQL、gRPC、tRPC 怎麼讀',
      },
    ],
  },
  {
    num: '05',
    code: 'RUNTIME',
    title: '容器化與維運監控',
    english: 'Containers, Probes & Deployment',
    range: 'Week 15 – 18',
    summary: 'Docker 容器化標準：GET /health 探針、結構化 Log 分析與期末真實服務交付。',
    aiFocus: '模型可以寫部署檔，但你要用健康檢查、Log 與外部 curl 驗收。',
    weeks: [
      { w: 15, dates: '12/14–12/20', title: '怎麼看 log' },
      { w: 16, dates: '12/21–12/27', title: '用 Docker 包起來', note: '12/25 行憲紀念日放假' },
      {
        w: 17,
        dates: '12/28–01/03',
        title: '專題整合 — 串起 API、資料庫與部署',
        href: '/lessons/17-vps-deployment',
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

export const aiCollaboration = {
  title: 'AI 可以幫忙，責任不能外包。',
  description:
    '你可以讓 AI 讀錯誤、找檔案、整理文件、提出 patch。你不能把「它說完成了」當成「系統已經正確」。這門課要求你把模型的建議，接回 HTTP、資料、權限與測試。',
  rules: [
    {
      number: '01',
      title: '先看，再問',
      detail: '先列出需求、現況、限制和你不知道的地方。模型沒有看到的檔案，不能假設它知道。',
      evidence: '留下：問題、相關檔案、待確認事項',
    },
    {
      number: '02',
      title: '資料只給必要的',
      detail:
        '`.env`、API key、Token、個人資料不要貼進 prompt。先用去識別化的範例，保留真正需要的上下文。',
      evidence: '留下：去識別化的上下文與資料來源',
    },
    {
      number: '03',
      title: '模型提案，Server 決定',
      detail: '模型可以提出程式或 tool call，但 schema、身份、授權與 allowlist 要在模型外檢查。',
      evidence: '留下：diff、權限判斷與執行結果',
    },
    {
      number: '04',
      title: '測試才算證據',
      detail: '跑測試、curl 和 log，對照 expected 與 actual；最後說明 AI 幫了哪裡、你改了哪裡。',
      evidence: '留下：指令、輸出、失敗與下一步',
    },
  ],
  sources: [
    {
      label: '臺大：生成式 AI 工具之教學因應措施',
      url: 'https://www.dlc.ntu.edu.tw/ai-tools/',
    },
    {
      label: '數位發展部：AI 產業人才認定指引',
      url: 'https://moda.gov.tw/ADI/services/publications/19692',
    },
  ],
} as const

export const backendCareerDirections = [
  {
    title: '後端與 API 開發',
    detail:
      '把 HTTP、路由、資料與錯誤處理串成服務。AI 可以先寫 handler，但你要看懂 Request／Response、寫測試，知道哪個 Status Code 代表什麼。',
    roles: '後端工程師、軟體設計工程師、系統分析師',
    sourceLabel: 'ColleGo! 資訊工程學類',
    source: 'https://collego.edu.tw/Highschool/MajorIntro?current_major_id=1',
  },
  {
    title: '資料庫與資料工程',
    detail:
      '把資料結構、交易、查詢與備份做穩。不是把 SQL 丟給模型，而是先知道資料怎麼進來、怎麼改變，出了錯怎麼回復。',
    roles: '資料庫管理人員、資料工程師、資料分析師',
    sourceLabel: 'ColleGo! 資訊管理學類',
    source: 'https://collego.edu.tw/Highschool/MajorIntro?current_college_id=1&current_major_id=7',
  },
  {
    title: '資安與網路',
    detail:
      '先問誰能進、能做什麼、哪一筆秘密不能出現。認證、授權、密鑰和網路入口，不能靠 prompt 保證。',
    roles: '資安工程師、網路安全工程師、網路管理工程師',
    sourceLabel: 'ColleGo! 資訊工程學類',
    source: 'https://collego.edu.tw/Highschool/MajorIntro?current_major_id=1',
  },
  {
    title: '雲端與系統維運',
    detail:
      '把 container、health check、log、firewall 和 HTTPS 接成一條能驗收的路。部署不是按一次按鈕，而是確認服務真的能被使用。',
    roles: '雲端服務工程、系統維運、資安／網路管理、技術支援',
    sourceLabel: '國發會：雲端服務產業人力需求',
    source: 'https://theme.ndc.gov.tw/manpower/cp.aspx?n=C9ECDD0E995DB66B',
  },
  {
    title: 'AI 應用與系統整合',
    detail:
      '把模型接到既有 API、資料和工具，不只是做一個聊天視窗。embedding、RAG、tool calling、eval 和 policy 都要回到後端的資料與權限邊界。',
    roles: 'AI 應用工程、後端整合、AI 解決方案規劃',
    sourceLabel: '數位發展部：AI 產業人才認定指引',
    source: 'https://moda.gov.tw/ADI/services/publications/19692',
  },
] as const
