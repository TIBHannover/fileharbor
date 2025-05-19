import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from '../plugins/axios'

import { useHelper } from '@/composables/helper'

export const useSearchStore = defineStore('search', () => {
  const resultList = ref([])
  const isLoading = ref(false)
  const jobId = ref(null)

  const queries = ref([])
  const globalWeights = ref([])

  function setGlobalWeights(newGlobalWeights) {
    globalWeights.value = newGlobalWeights
  }

  function setQueries(newQueries) {
    queries.value = newQueries
  }

  function search() {
    console.log(queries)
    let queriesWithWeights = queries.value.map((q) => {
      const helper = useHelper()
      if (helper.keyInObj(q, 'weights')) {
        return q
      }
      q.weights = globalWeights.value
      return q
    })

    const params = {
      queries: queriesWithWeights,
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
        jobId.value = null
        isLoading.value = false
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
        jobId.value = null
        isLoading.value = false
        // handle error
        console.log(error)
      })
  }

  return {
    resultList,
    isLoading,
    jobId,
    queries,
    setGlobalWeights,
    setQueries,
    search,
    fetchSearchResults,
  }
})
