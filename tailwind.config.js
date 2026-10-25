/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js",
    "./accounts/**/*.py",
    "./blog/**/*.py",
    "./courses/**/*.py",
    "./core/**/*.py",
    "./dashboard/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          DEFAULT: '#000000',
          bg: '#000000',
          surface: 'rgba(10, 10, 10, 0.94)',
          card: 'rgba(12, 12, 12, 0.95)',
          input: '#121212',
          'input-focus': '#181818',
          border: '#2a2a2a',
          muted: '#565656',
          subtle: '#777777',
          gray: '#a0a0a0',
        },
        cyan: {
          DEFAULT: '#00FFFF',
          glow: 'rgba(0, 255, 255, 0.35)',
          subtle: 'rgba(0, 255, 255, 0.12)',
          border: 'rgba(0, 255, 255, 0.4)',
        },
        aqua: {
          DEFAULT: '#00FFFF',
          5: 'rgba(0, 255, 255, 0.05)',
          10: 'rgba(0, 255, 255, 0.1)',
          20: 'rgba(0, 255, 255, 0.2)',
        },
        tomato: {
          DEFAULT: '#ff6347',
          glow: 'rgba(255, 99, 71, 0.45)',
          alert: 'rgba(255, 99, 71, 0.15)',
          border: '#ff6347',
        },
      },
      fontFamily: {
        righteous: ['Righteous', 'cursive', 'sans-serif'],
        lato: ['Lato', 'sans-serif'],
        roboto: ['Roboto', 'sans-serif'],
        patua: ['Patua One', 'cursive', 'sans-serif'],
      },
      boxShadow: {
        'cyan-glow': '0 0 20px rgba(0, 255, 255, 0.35)',
        'cyan-btn': '0 0 12px rgba(0, 255, 255, 0.3)',
        'cyan-card': '0 15px 40px rgba(0, 0, 0, 0.95), 0 0 30px rgba(0, 255, 255, 0.12)',
        'tomato-glow': '0 0 20px rgba(255, 99, 71, 0.45)',
        'tomato-btn': '0 0 15px rgba(255, 99, 71, 0.4)',
      },
      keyframes: {
        navlinkfade: {
          '0%': { opacity: '0', transform: 'translateX(50px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
      animation: {
        navlinkfade: 'navlinkfade 0.5s ease forwards',
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms')({ strategy: 'class' }),
    require('@tailwindcss/typography'),
  ],
}
