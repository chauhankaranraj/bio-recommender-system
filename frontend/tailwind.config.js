/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Deep-science palette inspired by genomics visualisation tools
        brand: {
          50:  '#eef8ff',
          100: '#d8eeff',
          200: '#b9e0ff',
          300: '#89cfff',
          400: '#52b4fd',
          500: '#2993fa',
          600: '#1373ef',
          700: '#0c5bdc',
          800: '#1149b2',
          900: '#14418c',
          950: '#112955',
        },
        surface: {
          DEFAULT: '#0f1629',
          card:    '#1a2340',
          border:  '#2a3560',
        },
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      backgroundImage: {
        'hero-gradient': 'radial-gradient(ellipse 120% 80% at 50% -10%, #1373ef33, transparent)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'fade-in':    'fadeIn 0.5s ease-in',
      },
      keyframes: {
        fadeIn: {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [],
}
