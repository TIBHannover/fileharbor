import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from '../plugins/axios'

export const useSearchStore = defineStore('search', () => {
  const resultList = ref([])
  const isLoading = ref(false)
  const jobId = ref(null)

  function search(query) {
    const params = {
      query: query,
    }
    axios
      .post('/search', { params })
      .then(({ data }) => {
        if (data.job_id !== undefined) {
          jobId.value = data.job_id
          isLoading.value = true
        } else {
          resultList.value = data.entries
          isLoading.value = false
          // commit('updateHits', data.entries);
          // commit('updateCounts', data.aggregations);
          // window.scrollTo(0, 0);
          // const status = { loading: false, error: false, timestamp: new Date() };
          // store.dispatch('utils/setStatus', status, { root: true });
        }
      })
      .catch(function (error) {
        // handle error
        console.log(error)
      })
  }

  function fetchSearchResults() {
    const params = { job_id: jobId.value }
    console.log(JSON.stringify({ fetchSearchResults: true, jobid: jobId.value }))

    axios
      .post('/search', { params })
      .then(({ data }) => {
        if (data.job_id !== undefined) {
          jobId.value = data.job_id
          isLoading.value = true
        } else {
          resultList.value = data.entries
          isLoading.value = false
          // commit('updateHits', data.entries);
          // commit('updateCounts', data.aggregations);
          // window.scrollTo(0, 0);
          // const status = { loading: false, error: false, timestamp: new Date() };
          // store.dispatch('utils/setStatus', status, { root: true });
        }
      })
      .catch(function (error) {
        // handle error
        console.log(error)
      })
  }

  return { search, fetchSearchResults, resultList, isLoading }
})
