/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#42B549',
          dark: '#2E8B34',
        },
        navy: '#071B31',
        ink: '#2D3A4D',
        card: {
          border: '#E5E7EB',
          title: '#0F172A',
          body: '#475569',
          meta: '#64748B',
        },
      },
    },
  },
  plugins: [],
}