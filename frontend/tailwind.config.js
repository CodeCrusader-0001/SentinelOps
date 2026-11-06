/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: '#0B0B10',
          surface: '#111118',
          card: '#151521',
          border: '#242436',
          cyan: '#00F2FE',
          blue: '#3B82F6',
          green: '#10B981',
          amber: '#F59E0B',
          rose: '#F43F5E',
          purple: '#8B5CF6',
        }
      }
    },
  },
  plugins: [],
}

