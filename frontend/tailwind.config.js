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
        phantom: {
          bg:     "#050A14",
          cyan:   "#00E5FF",
          accent: "#0D2137",
          alert:  "#FF3D00",
        },
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
