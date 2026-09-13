/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0F1726",        // deep navy base — academic, calm, serious
        surface: "#161F35",    // panel background
        surfaceAlt: "#1E2A45", // hover / secondary panel
        paper: "#F6F4EE",      // warm off-white for text on dark, and light-mode panels
        gold: "#C9A227",       // accent — achievement / distinction plan
        slate: "#8B96AE",      // secondary text
        success: "#4FAE7E",
        danger: "#C1554C",
      },
      fontFamily: {
        display: ["'Fraunces'", "serif"],
        body: ["'Public Sans'", "sans-serif"],
      },
    },
  },
  plugins: [],
};
