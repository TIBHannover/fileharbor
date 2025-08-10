import router from '@/router'

/**
 * Navigate to a route.
 * 
 * @param {string} name: Route name.
 * @param {boolean} [openInNewTab=false]: Whether to open a new browser tab.
 */
export default function useGoTo(name, openInNewTab = false) {
  try {
    const resolved = router.resolve({ name })
    if (openInNewTab) {
      window.open(resolved.href, '_blank')
    } else {
      router.push({ name })
    }
  } catch (error) {
    console.error('[useGoTo] Navigation failed:', error)
  }
}