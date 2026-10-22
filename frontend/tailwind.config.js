/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cream: "#FBF7EC",
        ink: "#0D0D0D",
        "ink-muted": "#4A4A4A",
        agent: "#4C8DFF",
        "agent-hover": "#6FA3FF",
        mint: "#3DDC97",
        "mint-hover": "#6BE8B1",
        warning: "#FFC233",
        danger: "#FF5A5F",
        navy: "#002E6E",
        trace: {
          bg: "#0D0D0D",
          text: "#E8F5E9",
          muted: "#9AA39E",
          blue: "#7FB0FF",
          green: "#5CF0A8",
          yellow: "#FFD56B",
          red: "#FF8A8D"
        }
      },
      fontFamily: {
        heading: ["'Space Grotesk'", "sans-serif"],
        body: ["'DM Sans'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        'brutal': '4px 4px 0 #0D0D0D',
        'brutal-lg': '8px 8px 0 #0D0D0D',
        'brutal-sm': '2px 2px 0 #0D0D0D',
      }
    },
  },
  plugins: [],
}
