import { ref } from 'vue'

/**
 * Helper for determining resource-specific values.
 * 
 * @returns {
 *   isLoaded: import('vue').Ref<boolean>,
 *   isDisabled: import('vue').Ref<boolean>,
 *   onLoad: () => void,
 *   onError: () => void
 * }
 */
export default function useResource() {
  const isLoaded = ref(false)
  function onLoad() {
    isLoaded.value = true
  }

  const isDisabled = ref(false)
  function onError() {
    isDisabled.value = true
  }

  return {
    isLoaded,
    isDisabled,
    onLoad,
    onError
  }
}