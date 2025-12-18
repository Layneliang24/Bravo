/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      animation: {
        'pulse-slow': 'pulse-slow 8s ease-in-out infinite',
        float: 'float 15s ease-in-out infinite',
        scan: 'scan 6s linear infinite',
        glow: 'glow 8s ease-in-out infinite',
        'glow-delayed': 'glow-delayed 8s ease-in-out infinite',
        'code-float': 'code-float 5s ease-in-out infinite',
        'spin-slow': 'spin-slow 20s linear infinite',
        'spin-reverse': 'spin 15s linear infinite reverse',
        orbit: 'orbit 4s ease-in-out infinite',
        'orbit-rotate': 'orbit-rotate 4s ease-in-out infinite',
        'char-wave': 'char-wave 2s ease-in-out infinite',
        'ping-slow': 'ping-slow 3s ease-in-out infinite',
        'bulb-pulse': 'bulb-pulse 2s ease-in-out infinite',
      },
      keyframes: {
        'pulse-slow': {
          '0%, 100%': { opacity: '0.3' },
          '50%': { opacity: '0.6' },
        },
        float: {
          '0%, 100%': {
            transform: 'translate(0, 0) scale(0)',
            opacity: '0',
          },
          '50%': {
            transform: 'translate(var(--tx, 0), var(--ty, -50px)) scale(1)',
            opacity: '1',
          },
        },
        scan: {
          '0%': { top: '0%' },
          '100%': { top: '100%' },
        },
        glow: {
          '0%, 100%': {
            transform: 'scale(1)',
            opacity: '0.1',
          },
          '50%': {
            transform: 'scale(1.2)',
            opacity: '0.2',
          },
        },
        'glow-delayed': {
          '0%, 100%': {
            transform: 'scale(1.2)',
            opacity: '0.2',
          },
          '50%': {
            transform: 'scale(1)',
            opacity: '0.1',
          },
        },
        'code-float': {
          '0%, 100%': {
            transform: 'translateY(0)',
            opacity: '0.1',
          },
          '50%': {
            transform: 'translateY(-30px)',
            opacity: '0.3',
          },
        },
        'spin-slow': {
          from: {
            transform: 'rotate(0deg)',
            opacity: '0.1',
          },
          '50%': {
            opacity: '0.3',
          },
          to: {
            transform: 'rotate(360deg)',
            opacity: '0.1',
          },
        },
        orbit: {
          '0%, 100%': {
            transform:
              'translate(calc(cos(var(--orbit-angle)) * 120px), calc(sin(var(--orbit-angle)) * 120px))',
            opacity: '0.9',
          },
          '50%': {
            opacity: '1',
          },
        },
        'orbit-rotate': {
          '0%': {
            transform: 'rotate(0deg) translateX(120px) rotate(0deg)',
          },
          '100%': {
            transform: 'rotate(360deg) translateX(120px) rotate(-360deg)',
          },
        },
        'char-wave': {
          '0%, 100%': {
            transform: 'translateY(0) rotate(var(--char-rotate, 0deg))',
          },
          '50%': {
            transform: 'translateY(-4px) rotate(var(--char-rotate, 0deg))',
          },
        },
        'ping-slow': {
          '0%': {
            transform: 'scale(0.8)',
            opacity: '1',
          },
          '50%': {
            transform: 'scale(1.2)',
            opacity: '0.5',
          },
          '100%': {
            transform: 'scale(0.8)',
            opacity: '1',
          },
        },
        'bulb-pulse': {
          '0%, 100%': {
            transform: 'scale(1)',
            opacity: '1',
          },
          '50%': {
            transform: 'scale(1.15)',
            opacity: '0.9',
          },
        },
      },
    },
  },
  plugins: [],
}
