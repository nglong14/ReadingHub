/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Vintage primary browns
                vintage: {
                    leather: '#382110',
                    'leather-light': '#5c4033',
                    'leather-dark': '#2a1810',
                    mahogany: '#4a3728',
                },
                // Cream and beige backgrounds
                parchment: {
                    light: '#FFF8F0',
                    DEFAULT: '#F9F7F4',
                    dark: '#F4F1EA',
                    cream: '#E8E2D5',
                },
                // Accent colors
                accent: {
                    orange: '#D6491A',
                    'orange-dark': '#B8401A',
                    gold: '#C9A961',
                    'gold-light': '#D4B86A',
                    star: '#EE8A00',
                },
                // Text colors
                ink: {
                    dark: '#333333',
                    medium: '#4a4a4a',
                    light: '#767676',
                    muted: '#999999',
                }
            },
            fontFamily: {
                serif: ['Merriweather', 'Georgia', 'serif'],
                sans: ['Lato', 'Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
            },
            boxShadow: {
                'vintage': '0 2px 8px rgba(56, 33, 16, 0.15)',
                'vintage-lg': '0 4px 16px rgba(56, 33, 16, 0.2)',
                'card': '0 1px 3px rgba(0, 0, 0, 0.1)',
                'card-hover': '0 4px 12px rgba(0, 0, 0, 0.15)',
                'book': '3px 3px 8px rgba(0, 0, 0, 0.3)',
            },
            borderRadius: {
                'vintage': '4px',
                'pill': '50px',
            },
            backgroundImage: {
                'leather-gradient': 'linear-gradient(135deg, #382110 0%, #5c4033 50%, #4a3728 100%)',
                'parchment-gradient': 'linear-gradient(180deg, #FFF8F0 0%, #F4F1EA 100%)',
                'gold-gradient': 'linear-gradient(135deg, #C9A961 0%, #D4B86A 100%)',
            },
            animation: {
                'float': 'float 3s ease-in-out infinite',
                'spin-slow': 'spin 2s linear infinite',
            },
            keyframes: {
                float: {
                    '0%, 100%': { transform: 'translateY(0px)' },
                    '50%': { transform: 'translateY(-5px)' },
                }
            }
        },
    },
    plugins: [],
}
