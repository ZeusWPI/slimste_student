import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { applyTheme, theme } from './config/theme'

// PrimeVue imports
import PrimeVue from 'primevue/config'
import Aura from '@primevue/themes/aura'
import 'primeicons/primeicons.css'

// Apply custom theme
applyTheme()

const app = createApp(App)

app.use(router)
app.use(PrimeVue, {
    theme: {
        preset: Aura,
        options: {
            darkModeSelector: true,
            cssLayer: false
        }
    }
})

// Override PrimeVue CSS variables with our theme
const style = document.createElement('style')
style.textContent = `
  :root {
    --p-primary-50: ${theme.primaryLight};
    --p-primary-100: ${theme.primaryLight};
    --p-primary-200: ${theme.primaryLight};
    --p-primary-300: ${theme.primaryLight};
    --p-primary-400: ${theme.primaryLight};
    --p-primary-500: ${theme.primary};
    --p-primary-600: ${theme.primary};
    --p-primary-700: ${theme.primaryDark};
    --p-primary-800: ${theme.primaryDark};
    --p-primary-900: ${theme.primaryDark};
    --p-primary-950: ${theme.primaryDark};
  }
`
document.head.appendChild(style)

app.mount('#app')
