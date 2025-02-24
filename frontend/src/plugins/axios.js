import axios from 'axios';
import store from '@/store';
import { API_LOCATION } from '@/../app.config';

const exclude_requests = ['/list_collection', '/search'];

const instance = axios.create({
  baseURL: API_LOCATION,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

instance.interceptors.request.use((request) => {
  if (!exclude_requests.includes(request.url)) {
    const status = { loading: true, error: false, timestamp: null };
    store.dispatch('utils/setStatus', status);
  }
  return request;
});

instance.interceptors.response.use((response) => {
  if (!exclude_requests.includes(response.config.url)) {
    const status = { loading: false, error: false, timestamp: new Date() };
    store.dispatch('utils/setStatus', status);
  }
  return response;
}, ({ response }) => {
  const status = { loading: false, error: true, timestamp: new Date() };
  store.dispatch('utils/setStatus', status);
  const message = { type: 'error', timestamp: new Date() };
  message.details = [response.data.detail] || ['unknown_error'];
  if (message.details[0] !== 'not_authenticated') {
    store.dispatch('utils/setMessage', message);
  }
  return new Promise(() => { });
});

export default instance;
