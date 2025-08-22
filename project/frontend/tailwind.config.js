/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: { 
        kuistoOrange: '#F18701' 
      },
      fontFamily: {
        montserrat: ['Montserrat', 'sans-serif'],
      },
      spacing: {
        '55': '219px',
      }
    },
  },
  plugins: [],
};