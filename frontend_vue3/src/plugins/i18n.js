import { createI18n } from 'vue-i18n'

function loadLocaleMessages() {
  const modules = import.meta.glob('@/locales/*.json', { eager: true })
  const messages = {}
  for (const path in modules) {
    const match = path.match(/\/([^/]+)\.json$/)
    if (!match) continue
    const module = modules[path]
    messages[match[1]] = module.default ?? module
  }
  return messages
}

function getBrowserLocale(countryCodeOnly = false) {
  const navLocale =
    navigator.languages?.[0] ||
    navigator.language ||
    navigator.userLanguage ||
    ''
  if (!navLocale) return
  const normalized = navLocale.trim()
  return countryCodeOnly
    ? normalized.split(/[-_]/, 1)[0]
    : normalized
}

const messages = loadLocaleMessages()
const availableLocales = Object.keys(messages)

function getStartingLocale() {
  const browserLocale = getBrowserLocale(true)
  if (browserLocale && availableLocales.includes(browserLocale)) {
    return browserLocale
  }
  return (
    import.meta.env.VUE_APP_I18N_LOCALE?.toString() ??
    'en'
  )
}

export default createI18n({
  legacy: false,
  locale: getStartingLocale(),
  fallbackLocale:
    import.meta.env.VUE_APP_I18N_FALLBACK_LOCALE?.toString() ??
    'en',
  messages,
})