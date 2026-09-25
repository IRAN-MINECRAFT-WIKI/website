/** @type {import('tailwindcss').Config} */
import typography from '@tailwindcss/typography';
import forms from '@tailwindcss/forms';

export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,ts,tsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // MineBed palette (kept consistent with original site)
        mc: {
          bg: '#0d0d18',
          'bg-2': '#14142a',
          panel: '#1c1c34',
          'panel-2': '#242445',
          line: '#2e2e4a',
          text: '#e6e6f2',
          'text-2': '#9a9ab8',
          'text-3': '#5c5c7a',
          grass: '#5fa838',
          'grass-2': '#7cc84a',
          'grass-3': '#3d7521',
          dirt: '#79553a',
          'dirt-2': '#5b3f29',
          stone: '#7d7d7d',
          gold: '#fcb32b',
          diamond: '#4aedd9',
          redstone: '#ff3b3b',
          emerald: '#17dd62',
        },
      },
      fontFamily: {
        sans: ['Vazirmatn', 'system-ui', 'sans-serif'],
        pixel: ['"Press Start 2P"', 'monospace'],
      },
      boxShadow: {
        'mc': '0 4px 0 rgba(0,0,0,0.45)',
        'mc-sm': '0 3px 0 rgba(0,0,0,0.4)',
      },
      backgroundImage: {
        'grass-top': 'linear-gradient(180deg, #6db73f 0 8px, #79553a 8px 100%)',
      },
    },
  },
  plugins: [typography, forms],
};
