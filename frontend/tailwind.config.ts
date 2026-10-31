import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        muted: "#5b6472",
        line: "#d9dee7",
        panel: "#ffffff",
        accent: "#0f766e",
        amber: "#b45309",
      },
      boxShadow: {
        soft: "0 18px 45px rgba(23,32,42,0.08)",
      },
    },
  },
  plugins: [],
} satisfies Config;

