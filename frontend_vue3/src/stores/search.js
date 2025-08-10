import { ref } from 'vue'
import { defineStore } from 'pinia'
import axios from '@/plugins/axios'

export const useSearchStore = defineStore('search', () => {
  const jobId = ref(null)
  const entries = ref([])
  const aggregations = ref([])

  function post() {
    const params = { } // TODO
    axios.post('/search', { params })
      .then(({ data }) => {
        if (data.job_id !== undefined) {
          jobId.value = data.job_id
          setTimeout(() => checkLoad, 500);
        } else {
          entries.value = data.entries
          aggregations.value = data.aggregations
        }
      })
  }

  function checkPost({ commit, dispatch, state }) {
    const params = { job_id: state.jobId }
    axios.post('/search', { params })
      .then(({ data }) => {
        if (data.job_id !== undefined) {
          jobId.value = data.job_id
          setTimeout(() => checkLoad, 500);
        } else {
          entries.value = data.entries
          aggregations.value = data.aggregations
        }
    })
  }

  return {
    entries,
    aggregations,
    post
  }
})