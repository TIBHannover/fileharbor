import axios from '@/plugins/axios';
import router from '@/router';

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i += 1) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === `${name}=`) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const user = {
  namespaced: true,
  state: {
    drawer: {
      settings: true,
      filter: false,
    },
    modal: {
      weights: false,
      layout: false,
      cluster: false,
    },
    userData: {},
    loggedIn: false,
    csrfToken: getCookie('csrftoken'),
  },
  actions: {
    getCSRFToken({ commit, state }, params) {
      axios.get('/get_csrf_token', {
        params, withCredentials: true,
      })
        .then(() => {
          const csrftoken = getCookie('csrftoken');
          if (state.csrfToken !== csrftoken) {
            commit('updateCSRFToken', csrftoken);
          }
        });
    },
    getUserData({ commit }, params) {
      axios.post('/get_user', { params })
        .then(({ data }) => {
          commit('updateUserData', data);
          commit('updateLoggedIn', true);
        });
    },
    login({ commit }, params) {
      axios.post('/login', { params })
        .then(({ data }) => {
          commit('updateUserData', data);
          commit('updateLoggedIn', true);
        });
    },
    logout({ commit, state }) {
      const params = state.userData;
      axios.post('/logout', { params })
        .then(() => {
          commit('updateUserData', {});
          commit('updateLoggedIn', false);
          router.replace({ path: '/' })
        });
    },
    register({ commit }, params) {
      axios.post('/register', { params })
        .then(({ data }) => {
          commit('updateUserData', data);
          commit('updateLoggedIn', true);
        });
    },
  },
  mutations: {
    updateLoggedIn(state, loggedIn) {
      state.loggedIn = loggedIn;
    },
    updateUserData(state, userData) {
      state.userData = userData;
    },
    updateCSRFToken(state, token) {
      state.csrfToken = token;
    },
    toggleDrawer(state, drawer) {
      state.drawer[drawer] = !state.drawer[drawer];
    },
    updateDrawer(state, { drawer, value }) {
      state.drawer[drawer] = value;
    },
    updateAllDrawers(state, value) {
      Object.keys(state.drawer).forEach((drawer) => {
        state.drawer[drawer] = value;
      });
    },
    toggleModal(state, modal) {
      state.modal[modal] = !state.modal[modal];
    },
    updateModal(state, { modal, value }) {
      state.modal[modal] = value;
    },
    updateAllModals(state, value) {
      Object.keys(state.modal).forEach((modal) => {
        state.modal[modal] = value;
      });
    },
  },
};

export default user;
