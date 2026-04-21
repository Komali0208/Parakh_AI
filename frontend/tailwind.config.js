/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class', // enable class-based dark mode
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // custom accent colors if needed
        accent: 'hsl(var(--accent))',
      },
    },
  },
  plugins: [],
};
