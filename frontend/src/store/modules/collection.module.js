import axios from '@/plugins/axios';

const collection = {
  namespaced: true,
  state: {
    collections: [],
    modal: {
      list: false,
    },
  },
  actions: {
    upload(context, params) {
      const formData = new FormData();
      formData.append('image', params.image);
      formData.append('meta', params.meta);
      formData.append('name', params.name);
      axios.post('/add_collection', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
    },
    delete({ dispatch }, params) {
      axios.post('/remove_collection', { params })
        .then(() => {
          dispatch('list');
        });
    },
    list({ commit }) {
      axios.get('/list_collection')
        .then(({ data }) => {
          commit('updateCollections', data);
        });
    },
  },
  mutations: {
    updateCollections(state, collections) {
      state.collections = collections;
    },
    updateModal(state, { modal, value }) {
      state.modal[modal] = value;
    },
  },
};

export default collection;
