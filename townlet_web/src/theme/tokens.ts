export const tokens = {
  color: {
    background: "#0d1117",
    surface: "#161b22",
    accent: "#3fb950",
    accentWarning: "#f0883e",
    accentDanger: "#f85149",
    textPrimary: "#c9d1d9",
    textMuted: "#8b949e"
  },
  typography: {
    fontFamily: "'Inter', 'Segoe UI', sans-serif",
    baseSizePx: 14,
    lineHeights: {
      tight: 1.2,
      default: 1.5,
      spacious: 1.8
    }
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 12,
    lg: 16,
    xl: 24
  },
  metrics: {
    cardMinWidth: 320,
    navHeight: 56,
    chartRefreshMs: 1000
  }
} as const;

export type Tokens = typeof tokens;
