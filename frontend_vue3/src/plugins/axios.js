import axios from 'axios';

const API_LOCATION = 'http://localhost:8000';

const instance = axios.create({
  baseURL: API_LOCATION,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

instance.interceptors.request.use((request) => {
  return request;
});

instance.interceptors.response.use((response) => {
  return response;
}, ({ response }) => {
  const message = { type: 'error', timestamp: new Date() };
  message.details = [response.data.detail || 'unknown_error'];
  return new Promise(() => { });
});

export default instance;
