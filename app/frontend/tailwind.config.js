/** @type {import('tailwindcss').Config} */
module.exports = {
  // Use the .dark class for dark mode, which our ThemeContext provides.
  darkMode: 'class',

  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}"
  ],

  // Keep this for Ant Design compatibility.
  corePlugins: {
    preflight: false,
  },

  // === THIS IS THE CRUCIAL UPDATE ===
  // We extend the default Tailwind theme with our own design tokens.
  // This makes our CSS variables from global.css available as utility classes.
  theme: {
    extend: {
      colors: {
        // Brand Accent
        primary: 'var(--color-primary)',
        'primary-hover': 'var(--color-primary-hover)',
        'primary-text': 'var(--color-primary-text)',

        // Surface / Background
        'bg-base': 'var(--color-bg-base)',
        'ui-base': 'var(--color-ui-base)',
        'ui-hover': 'var(--color-ui-hover)',
        'ui-active': 'var(--color-ui-active)',

        // Borders
        border: 'var(--color-border)',

        // Text
        'text-base': 'var(--color-text-base)',
        'text-muted': 'var(--color-text-muted)',
        
        // Exposing AntD's theme colors for utility classes if needed
        success: 'var(--ant-color-success)',
        warning: 'var(--ant-color-warning)',
        error: 'var(--ant-color-error)',
        info: 'var(--ant-color-info)',
      },
      boxShadow: {
        sm: 'var(--shadow-sm)',
        md: 'var(--shadow-md)',
        lg: 'var(--shadow-lg)',
      },
      borderRadius: {
        // Matching Ant Design tokens for consistency
        DEFAULT: '6px', // antd's borderRadius
        lg: '12px',      // antd's borderRadiusLG
      },
      fontFamily: {
        // We can define this here to ensure it's used by Tailwind utilities
        sans: ['Inter', 'sans-serif'],
      }
    },
  },

  plugins: [],
}