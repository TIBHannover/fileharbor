import { ref, computed } from 'vue'
import i18n from '@/plugins/i18n'

/**
 * Helper for determining resource-specific values.
 * 
 * @returns {
 *   isLoaded: import('vue').Ref<boolean>,
 *   isDisabled: import('vue').Ref<boolean>,
 *   onLoad: () => void,
 *   onError: () => void,
 *   titles: ,
 *   creators: ,
 *   metadata: 
 * }
 */
export default function useResource(item) {
  const isLoaded = ref(false)
  function onLoad() {
    isLoaded.value = true
  }

  const isDisabled = ref(false)
  function onError() {
    isDisabled.value = true
  }

  const { t } = i18n.global

  const getMetaValues = (key, toInt = false) => {
    const values = item.meta
      .filter(m => m && m.name && m.value_str)
      .filter(m => m.name === key)
      .map(m => {
        let val = String(m.value_str).trim();
        if (toInt) {
          const parsed = parseInt(val, 10);
          return isNaN(parsed) ? null : parsed;
        }
        return val;
      })
      .filter(Boolean)

    return [...new Set(values)]
  }

  const titles = computed(() => {
    const values = getMetaValues('title')
    return values.length ? values : [t('resource.field.meta.title')]
  })

  const creators = computed(() => {
    const values = getMetaValues('artist_name')
    return values.length ? values : [t('resource.field.meta.artist_name')]
  })

  const years = computed(() => {
    const mins = getMetaValues('year_min', true)
    const maxs = getMetaValues('year_max', true)

    const min = mins.length ? Math.min(...mins) : -9999
    const max = maxs.length ? Math.max(...maxs) : 9999
    return [min, max]
  })

  const metadata = computed(() => {
    const excluded = new Set([
      'license',
      'title',
      'url',
      'wikidata',
      'year_min',
      'year_max'
    ])

    const result = {}
    for (const { name, value_str } of item.meta) {
      if (!excluded.has(name) && value_str) {
        const trimmed = value_str.toString().trim()
        if (result[name]) {
          result[name].push(trimmed)
        } else {
          result[name] = [trimmed]
        }
      }
    }
    return result
  })

  return {
    isLoaded,
    isDisabled,
    onLoad,
    onError,
    titles,
    creators,
    years,
    metadata
  }
}