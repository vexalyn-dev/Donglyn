/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#050505",
          elevated: "#0d0d0d",
          surface: "#101010",
          card: "#151515",
          hover: "#181818",
        },
        foreground: {
          DEFAULT: "#f5f5f5",
          muted: "#a1a1aa",
          dim: "#71717a",
        },
        donglyn: {
          DEFAULT: "#e50914",
          bright: "#ff1a24",
          deep: "#8b0000",
        },
        border: {
          DEFAULT: "rgba(255,255,255,0.06)",
          strong: "rgba(255,255,255,0.10)",
          red: "rgba(229,9,20,0.35)",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Bebas Neue", "system-ui", "sans-serif"],
      },
      borderRadius: {
        xl: "12px",
        XXL: "16px",
        XXXL: "20px",
      },
      boxShadow: {
        card: "0 4px 24px rgba(0,0,0,0.4)",
        cardHover: "0 8px 32px rgba(0,0,0,0.5), 0 0 0 1px rgba(229,9,20,0.1)",
      },
      animation: {
        "spin-slow": "spin 3s linear infinite",
      },
    },
  },
  plugins: [
    require("@tailwindcss/forms"),
    function ({ addUtilities }) {
      addUtilities({
        ".line-clamp-1": {
          overflow: "hidden",
          display: "-webkit-box",
          "-webkit-box-orient": "vertical",
          "-webkit-line-clamp": "1",
          line-clamp: "1",
        },
        ".line-clamp-2": {
          overflow: "hidden",
          display: "-webkit-box",
          "-webkit-box-orient": "vertical",
          "-webkit-line-clamp": "2",
          line-clamp: "2",
        },
        ".line-clamp-3": {
          overflow: "hidden",
          display: "-webkit-box",
          "-webkit-box-orient": "vertical",
          "-webkit-line-clamp": "3",
          line-clamp: "3",
        },
        ".scrollbar-hide": {
          "-ms-overflow-style": "none",
          "scrollbar-width": "none",
        },
        ".scrollbar-hide::-webkit-scrollbar": {
          display: "none",
        },
      });
    },
  ],
};
