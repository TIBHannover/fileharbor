import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'

export const useSearchStore = defineStore('search', () => {
  let params = {}
  let filters = {}

  const jobId = ref(null)
  const entries = ref([])
  const aggregations = ref([])

  function post(newParams = {}) {
    const mergedParams = {
      ...params,
      ...newParams,
      dataset: newParams.dataset ?? params.dataset,
      similarity: newParams.similarity ?? params.similarity,
    }

    params = mergedParams
    const body = { ...mergedParams, filters }

    axios.post('/search', { params: body }).then(({ data }) => {
      if (data.job_id !== undefined) {
        jobId.value = data.job_id
        setTimeout(() => checkPost(), 500)
      } else {
        entries.value = data.entries
        aggregations.value = data.aggregations
      }
    })
  }

  function checkPost() {
    const body = { job_id: jobId.value }
    axios.post('/search', { params: body }).then(({ data }) => {
      if (data.job_id !== undefined) {
        jobId.value = data.job_id
        setTimeout(() => checkPost(), 500)
      } else {
        entries.value = data.entries
        aggregations.value = data.aggregations
      }
    })
  }

  function setFilters(values) {
    filters = { ...values }
  }

  function removeFilters() {
    filters = {}
  }

  return {
    entries,
    aggregations,
    post,
    checkPost,
    setFilters,
    removeFilters,
  }
})
