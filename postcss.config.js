module.exports = {
  plugins: [
    // Tailwind v4 requires the dedicated PostCSS plugin package
    // see error message: install @tailwindcss/postcss and use it here
    require('@tailwindcss/postcss'),
    require('autoprefixer'),
  ]
}
