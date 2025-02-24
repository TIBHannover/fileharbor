import mixins from '@/mixins';
import axios from '@/plugins/axios';

const bookmark = {
  namespaced: true,
  state: {
    history: [],
    bookmarks: [],
    toggle: false,
  },
  actions: {
    add({ commit, rootState }, params) {
      if (rootState.user.loggedIn) {
        axios.post('/add_bookmark', { params });
      }
      commit('add', params);
    },
    remove({ commit, rootState }, params) {
      if (rootState.user.loggedIn) {
        axios.post('/remove_bookmark', { params });
      }
      commit('remove', params);
    },
    list({ commit, rootState }, params) {
      if (rootState.user.loggedIn) {
        axios.post('/list_bookmark', { params })
          .then(({ data }) => {
            commit('set', data);
          });
      }
    },
  },
  mutations: {
    update(state, value) {
      state.toggle = value;
    },
    add(state, { id }) {
      let index = state.bookmarks.indexOf(id);
      if (index === -1) {
        state.bookmarks.push(id);
      }
      index = state.history[0].bookmarks.indexOf(id);
      if (index === -1) {
        state.history[0].bookmarks.push(id);
      }
    },
    remove(state, { id }) {
      let index = state.bookmarks.indexOf(id);
      if (index !== -1) {
        state.bookmarks.splice(index, 1);
      }
      index = state.history[0].bookmarks.indexOf(id);
      if (index !== -1) {
        state.history[0].bookmarks.splice(index, 1);
      }
    },
    set(state, values) {
      state.bookmarks = [];
      values.forEach(({ id }) => {
        const index = state.bookmarks.indexOf(id);
        if (index === -1) {
          state.bookmarks.push(id);
        }
      });
    },
    addHistory(state, params) {
      params = mixins.methods.stringify(params);
      params = JSON.parse(params);
      const validKeys = [
        'query', 'random', 'filters',
        'full_text', 'date_range',
      ];
      Object.keys(params).forEach((key) => {
        if (!validKeys.includes(key)) {
          delete params[key];
        }
      });
      const hash = mixins.methods.getHash(params);
      const hashes = state.history.map((x) => x.hash);
      const index = hashes.indexOf(hash);
      if (index !== -1) {
        params.bookmarks = state.history[index].bookmarks;
        state.history.splice(index, 1);
      } else {
        params.bookmarks = [];
      }
      state.history.unshift({ date: Date(), ...params, hash });
    },
    removeHistory(state, params) {
      const index = state.history.indexOf(params);
      if (index !== -1) {
        state.history.splice(index, 1);
      }
    },
    removeAllHistory(state) {
      state.history = [];
    },
  },
};

export default bookmark;
