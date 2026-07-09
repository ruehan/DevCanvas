import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#FAF9F5",
        "bg-soft": "#F5F4EE",
        surface: "#FFFFFF",
        "surface-alt": "#F0EEE6",
        "surface-deep": "#EAE7DC",
        border: "#E5E2D8",
        "border-strong": "#DAD6CB",
        text: "#1F1E1D",
        "text-soft": "#2D2B27",
        "text-muted": "#6B6760",
        "text-faint": "#9A958B",
        accent: {
          DEFAULT: "#C96442",
          hover: "#B5533A",
          soft: "#F4E8E1",
        },
        success: {
          DEFAULT: "#5C8A4A",
          soft: "#E8EFE3",
        },
        danger: {
          DEFAULT: "#B5524A",
          soft: "#F2E3E1",
        },
        warn: "#B8893A",
      },
      fontFamily: {
        sans: ["GmarketSans", "sans-serif"],
        serif: ["GmarketSans", "sans-serif"],
        mono: ["var(--font-jbmono)", "JetBrains Mono", "ui-monospace", "monospace"],
      },
      fontSize: {
        "2xs": ["11px", "1.4"],
      },
    },
  },
  plugins: [],
};

export default config;
