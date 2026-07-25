export const historyData = [
  {
    id: 1,
    day: "Today",
    type: "review",
    title: "Security Review: auth-service",
    description:
      "Audit of OAuth2 callback controller in backend-core. All 12 vulnerabilities addressed.",
    time: "14:32",
    ago: "2h ago",
    ticket: "KRV-9012",
    status: "success",
  },
  {
    id: 2,
    day: "Today",
    type: "translation",
    title: "Sync: dashboard-i18n locales",
    description:
      "Updating locale files for FR-fr and ES-es regions. 85% localized, waiting for manual validation.",
    time: "11:15",
    ago: "5h ago",
    ticket: "KTR-4421",
    status: "running",
  },
  {
    id: 3,
    day: "Yesterday",
    type: "repository",
    title: "Repo Sync: production-infra",
    description:
      "Webhook synchronization failed due to authentication timeout. Automatic retry scheduled.",
    time: "Yesterday, 18:45",
    ticket: "KSY-0092",
    status: "failed",
  },
  {
    id: 4,
    day: "Yesterday",
    type: "review",
    title: "PR Review: layout-v2 updates",
    description:
      "Implemented dark-mode support for complex navigation components. Approved by 2 senior reviewers.",
    time: "Yesterday, 09:20",
    ticket: "KRV-8810",
    status: "success",
  },
];

export const liveUsers = [
  {
    id: 1,
    initials: "JD",
    name: "Jane Doe",
    activity: "Reviewing 'backend-core'",
    online: true,
  },
  {
    id: 2,
    initials: "MS",
    name: "Marcus Smith",
    activity: "Syncing assets...",
    online: true,
  },
  {
    id: 3,
    initials: "KL",
    name: "Kathy Lin",
    activity: "Offline",
    online: false,
  },
];

export const historyStats = {
  itemsLogged: 128,
  automation: "82%",
};