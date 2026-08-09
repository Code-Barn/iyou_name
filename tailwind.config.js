/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './apps/**/templates/**/*.html',
    './templates/**/*.html',
    './apps/**/static/**/*.js',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      screens: {
        xs: '360px',
      },
    },
  },
  plugins: [],
}
