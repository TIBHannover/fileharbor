import { createApp } from 'vue'
import { createI18n } from 'vue-i18n';
import { createPinia } from 'pinia'

import 'vuetify/styles'
import '@mdi/font/css/materialdesignicons.css'

import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

import { aliases, mdi } from 'vuetify/iconsets/mdi'

import App from './App.vue'
import router from './router'


// function loadLocaleMessages() {
//     const locales = import.meta.glob('/*');
//     console.log(JSON.stringify(locales));
//     const messages = {};
//     locales.keys().forEach((key) => {
//         const matched = key.match(/([A-Za-z0-9-_]+)\./i);
//         if (matched && matched.length > 1) {
//             messages[matched[1]] = locales(key);
//         }
//     });
//     return messages;
// }

const i18n = createI18n({
    locale: 'en',
    messages: {},
});

const vuetify = createVuetify({
    theme: {
        defaultTheme: 'light'
    },
    icons: {
        defaultSet: 'mdi',
        aliases,
        sets: {
            mdi,
        },
    },
    components,
    directives,
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)
app.use(i18n)

app.mount('#app')
