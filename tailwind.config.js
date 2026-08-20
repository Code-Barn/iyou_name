/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './apps/**/templates/**/*.html',
    './templates/**/*.html',
    './static/**/*.js',
    './apps/**/static/**/*.js',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        onyx: '#0B0F19',
      },
      screens: {
        xs: '360px',
      },
    },
  },
  plugins: [],
}
