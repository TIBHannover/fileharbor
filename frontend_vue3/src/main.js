import { createApp } from 'vue'
import { createPinia } from 'pinia'
import i18n from '@/plugins/i18n'
import vuetify from '@/plugins/vuetify'
import App from '@/App.vue'
import router from '@/router'
import '@/styles/main.css'

createApp(App)
  .use(createPinia())
  .use(vuetify)
  .use(router)
  .use(i18n)
  .mount('#app')