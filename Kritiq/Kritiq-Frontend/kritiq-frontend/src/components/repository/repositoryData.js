export const repositories = [
  {
    id: 1,
    name: "kritiq-engine",
    status: "scanning",
    branch: "main",
    commit: "7f3a9e1",
    lastScan: "Oct 24, 14:20",
    language: "Go",
    progress: 68,
    progressLabel: "ANALYZING VULNERABILITIES",
  },
  {
    id: 2,
    name: "frontend-v3",
    status: "synced",
    branch: "develop",
    commit: "b120c4a",
    lastScan: "Oct 23, 09:12",
    language: "TypeScript",
  },
  {
    id: 3,
    name: "auth-service",
    status: "synced",
    branch: "main",
    commit: "e992b8d",
    lastScan: "Oct 21, 18:45",
    language: "Go",
  },
  {
    id: 4,
    name: "legacy-api",
    status: "failed",
    branch: "main",
    commit: "0c451e2",
    lastScan: "Never",
    language: "Python",
    error:
      "SSH Key authentication failed. Please update your repository credentials.",
  },
  {
    id: 5,
    name: "mobile-app-ios",
    status: "synced",
    branch: "release/v1.2",
    commit: "d7f8a1b",
    lastScan: "Oct 20, 11:30",
    language: "Swift",
  },
];

export const repositoryStats = [
  {
    title: "Total Repositories",
    value: "12",
  },
  {
    title: "Storage Used",
    value: "4.2 GB",
  },
  {
    title: "Total Scans",
    value: "1,482",
  },
  {
    title: "Sync Health",
    value: "98%",
    trend: true,
  },
];