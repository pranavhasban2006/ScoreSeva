/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          orange:      "#F97316",
          "orange-dark": "#EA6C0A",
          "orange-light": "#FED7AA",
          "orange-bg":  "#FFF7ED",
        },
        risk: {
          excellent: "#22C55E",
          good:      "#84CC16",
          fair:      "#F59E0B",
          poor:      "#F97316",
          verypoor:  "#EF4444",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        card: "0 1px 3px 0 rgba(0,0,0,0.07), 0 1px 2px -1px rgba(0,0,0,0.07)",
        "card-hover": "0 4px 12px 0 rgba(0,0,0,0.10)",
      },
    },
  },
  plugins: [],
}
