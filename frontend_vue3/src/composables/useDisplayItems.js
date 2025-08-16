import { computed, isRef } from 'vue'
import { storeToRefs } from 'pinia'
import { useDisplay } from 'vuetify'

/**
 * Helper for determining display-specific layout values.
 * 
 * @param {string} store: Pinia store instance.
 * @returns {
 *   itemsPerPage: import('vue').ComputedRef<number>,
 *   itemsPerRow: import('vue').ComputedRef<number>,
 *   noDataCols: import('vue').ComputedRef<number>
 * }
 */
export default function useDisplayItems(store) {
  const { name } = useDisplay()

  const refs = storeToRefs(store)
  const itemsPerPageRef = refs?.itemsPerPage

  const itemsPerPage = computed(() => {
    const value = isRef(itemsPerPageRef) ? itemsPerPageRef.value : store?.itemsPerPage
    return Number.isInteger(value) && value > 0 ? value : 96
  })

  const itemsPerRowMap = { xs: 1, sm: 2, md: 3, lg: 4, xl: 6, xxl: 6 }
  const itemsPerRow = computed(() => {
    const value = itemsPerRowMap[name.value]
    return Number.isInteger(value) && value > 0 ? value : 6
  })

  const noDataColsMap = { xs: 12, sm: 9, md: 6, lg: 4, xl: 3, xxl: 3 }
  const noDataCols = computed(() => {
    const value = noDataColsMap[name.value]
    return Number.isInteger(value) && value > 0 ? value : 3
  })

  return {
    itemsPerPage,
    itemsPerRow,
    noDataCols
  }
}