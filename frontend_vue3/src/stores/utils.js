import { reactive } from 'vue'
import { defineStore } from 'pinia'

export const useUtilsStore = defineStore('utils', () => {
  const status = reactive({
    error: false,
    loading: false,
    timestamp: null
  })

  const message = reactive({
    type: null,
    details: null,
    timestamp: null
  })

  function setStatus({ error, loading, timestamp }) {
    status.error = error
    status.loading = loading
    status.timestamp = timestamp
  }

  function setMessage({ type, details, timestamp }) {
    message.type = type
    message.details = details
    message.timestamp = timestamp
  }

  return {
    status,
    message,
    setStatus,
    setMessage
  }
})