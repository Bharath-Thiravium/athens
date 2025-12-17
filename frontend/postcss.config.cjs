// New and Correct configuration (for Tailwind v4)
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {}, // This is the only line that changes
    autoprefixer: {},
  },
};