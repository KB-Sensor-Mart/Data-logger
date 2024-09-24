/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
    animation: {
     'spin-once': 'spin 2s ease-in-out 1',
     'bounce-once': 'bounce 1s ease-in 2',
     'bounce': 'bounce 2s ease-in 2',
      }
},
  },
  plugins: [],
}

