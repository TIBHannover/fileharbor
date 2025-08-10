import 'vuetify/styles' 
import { createVuetify } from 'vuetify'
import '@mdi/font/css/materialdesignicons.css'

export default createVuetify({
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1d3556',
          secondary: '#cdcdcd',
          accent: '#f7f8fb',
          error: '#e63946',
          surface: '#fff',
          background: '#fff'
        }
      }
    }
  }
})