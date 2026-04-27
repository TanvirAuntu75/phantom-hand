/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: "#050A14",
        primary: "#00E5FF",
        secondary: "#FFD700",
        structure: "#0D47A1",
        dim: "#4A7FA5",
        inactive: "#0D2137",
        leftHand: "#FF00C8",
        rightHand: "#00E5FF",
        ghostRed: "#800000"
      },
      fontFamily: {
        mono: ['"Share Tech Mono"', 'monospace'],
      },
      borderRadius: {
        none: '0px',
        sm: '0px',
        DEFAULT: '0px',
        md: '0px',
        lg: '0px',
        xl: '0px',
        '2xl': '0px',
        '3xl': '0px',
        full: '0px',
      }
    },
  },
  plugins: [],
}
