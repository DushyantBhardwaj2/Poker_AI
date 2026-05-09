/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      colors: {
        gold: {
          DEFAULT: '#D4AF37',
          light: '#F4D03F',
          dark: '#B8960C',
        },
        amber: {
          warm: '#FFA500',
        },
        charcoal: {
          DEFAULT: '#1A1A1A',
          light: '#2D2D2D',
          dark: '#0D0D0D',
        },
        cream: {
          DEFAULT: '#F5F5DC',
          dark: '#E8E8D0',
        },
      },
      fontFamily: {
        display: ['Playfair Display', 'serif'],
        sans: ['DM Sans', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'slide-up': 'slideUp 0.6s ease-out',
        'scale-in': 'scaleIn 0.4s ease-out',
        'pulse-gold': 'pulseGold 2s ease-in-out infinite',
        'card-deal': 'cardDeal 0.4s ease-out',
        'chip-throw': 'chipThrow 0.5s ease-out',
        'stagger': 'staggerIn 0.3s ease-out forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.95)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        pulseGold: {
          '0%, 100%': {
            borderColor: 'rgba(212, 175, 55, 0.4)',
            boxShadow: '0 0 15px rgba(212, 175, 55, 0.2)'
          },
          '50%': {
            borderColor: 'rgba(212, 175, 55, 0.8)',
            boxShadow: '0 0 25px rgba(212, 175, 55, 0.3)'
          },
        },
        cardDeal: {
          '0%': { opacity: '0', transform: 'translateX(-100px) rotate(-20deg)' },
          '60%': { transform: 'translateX(10px) rotate(5deg)' },
          '100%': { opacity: '1', transform: 'translateX(0) rotate(0)' },
        },
        chipThrow: {
          '0%': { transform: 'scale(0) translateY(-50px)', opacity: '0' },
          '50%': { transform: 'scale(1.2) translateY(0)', opacity: '1' },
          '75%': { transform: 'scale(0.9)' },
          '100%': { transform: 'scale(1) translateY(0)', opacity: '1' },
        },
        staggerIn: {
          '0%': { opacity: '0', transform: 'translateY(15px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      boxShadow: {
        'gold': '0 0 15px rgba(212, 175, 55, 0.2)',
        'gold-strong': '0 0 30px rgba(212, 175, 55, 0.4)',
      },
    },
  },
  plugins: [],
}