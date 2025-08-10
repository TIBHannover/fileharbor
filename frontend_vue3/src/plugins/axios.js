import axios from 'axios'
import { useUtilsStore } from '@/stores/utils'

function resolveBaseURL() {
  const env = import.meta?.env?.VITE_APP_API
  if (!env) return 'http://localhost:8000'
  return /^https?:\/\//i.test(env) ? env : `https://${env}`
}

function normalizeToken(input) {
  return input.trim().replace(/\s+/g, '_').replace(/\./g, '').toLowerCase()
}

function hasJobIdPayload(payload) {
  try {
    if (payload && Object.prototype.toString.call(payload) === '[object Object]') {
      return Boolean(payload.job_id ?? payload.params?.job_id)
    }
  } catch {
    /* noop */
  }
  return false
}

const instance = axios.create({
  baseURL: resolveBaseURL(),
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
  timeout: 30_000
})

const setLoading = (on) =>
  useUtilsStore().setStatus({
    loading: on,
    error: false,
    timestamp: on ? null : new Date()
  })

const setError = () =>
  useUtilsStore().setStatus({
    loading: false,
    error: true,
    timestamp: new Date()
  })

instance.interceptors.request.use((config) => {
  const dataHasJob = hasJobIdPayload(config.data)
  const paramsHasJob = hasJobIdPayload(config.params)
  if (!dataHasJob && !paramsHasJob) setLoading(true)
  return config
})

instance.interceptors.response.use((response) => {
  if (!hasJobIdPayload(response?.data)) setLoading(false)
    return response
}, (error) => {
  setError()

  const utils = useUtilsStore()
  const message = {
    type: 'error',
    timestamp: new Date(),
    details: ['unknown_error']
  }

  const data = error.response?.data
  if (typeof data === 'string') {
    message.details = [normalizeToken(data)]
  } else if (Array.isArray(data)) {
    message.details = data.map((v) => normalizeToken(String(v))).filter(Boolean)
  } else if (data && typeof data === 'object') {
    const tokens = []
    for (const [_, raw] of Object.entries(data)) {
      const values = Array.isArray(raw) ? raw : [raw]
      values.forEach((v) => tokens.push(normalizeToken(String(v))))
    }
    if (tokens.length) message.details = tokens
  } else if (error.code === 'ECONNABORTED') {
    message.details = ['request_timeout']
  } else if (error.message) {
    message.details = [normalizeToken(error.message)]
  }

  utils.setMessage(message)

  return new Promise(() => {})
});

export default instance