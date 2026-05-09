/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/**/*.{js,jsx,ts,tsx}", "./src/**/*.{js,jsx,ts,tsx}"],
  presets: [require("nativewind/preset")],
  theme: {
    extend: {
      colors: {
        navy: { 900: "#0D183D" },
        blue: { 500: "#2563EB" },
        teal: { 500: "#10B981" },
        danger: "#EF4444",
        warning: "#F59E0B",
      },
    },
  },
  plugins: [],
};
