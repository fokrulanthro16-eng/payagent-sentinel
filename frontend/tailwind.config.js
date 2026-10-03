/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sentinel: {
          dark: '#080c14',
          panel: '#0e1726',
          border: '#1f293d',
          accent: '#0070ba',
          cyan: '#00e5ff',
          success: '#00d68f',
          danger: '#ff3d71',
          warning: '#ffaa00',
        }
      }
    },
  },
  plugins: [],
}
