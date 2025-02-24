import Vue from 'vue';
import store from '@/store';
import router from '@/router';
import mixins from '@/mixins';
import axios from '@/plugins/axios';
import config from '@/../app.config';
import { lsplit } from '@/plugins/helpers';

const api = {
  namespaced: true,
  state: {
    random: null,
    lang: 'en',
    query: [],
    dateRange: [],
    fullText: [],
    filters: {},
    counts: [],
    hits: undefined,
    settings: {
      weights: {},
      layout: {
        itemSize: 0,
        sortOrder: 'asc',
        sortType: 'relevance',
        viewGrid: false,
        viewType: 'flexible',
      },
      cluster: {},
    },
    prevParams: {},
    backBtn: false,
    jobID: null,
  },
  actions: {
    load({
      commit, dispatch, state, rootState,
    }) {
      const params = {
        lang: state.lang,
        query: state.query,
        random: state.random,
        filters: state.filters,
        settings: state.settings,
        full_text: state.fullText,
        date_range: state.dateRange,
        bookmarks: rootState.bookmark.toggle,
        aggregate: config.DEFAULT_AGGREGATION_FIELDS,
      };
      if (!mixins.methods.isEqual(params, state.prevParams)) {
        commit('updateParams', params);
        commit('bookmark/addHistory', params, { root: true });
        if (!state.backBtn) {
          dispatch('getState');
        } else {
          commit('toggleBackBtn');
        }
        const status = { loading: true, error: false, timestamp: null };
        store.dispatch('utils/setStatus', status, { root: true });
        axios.post('/search', { params })
          .then(({ data }) => {
            if (data.job_id !== undefined) {
              commit('updateJobID', data.job_id);
              setTimeout(() => dispatch('checkLoad'), 500);
            } else {
              commit('updateHits', data.entries);
              commit('updateCounts', data.aggregations);
              window.scrollTo(0, 0);
              const status = { loading: false, error: false, timestamp: new Date() };
              store.dispatch('utils/setStatus', status, { root: true });
            }
          });
      }
    },
    checkLoad({ commit, dispatch, state }) {
      const params = { job_id: state.jobID };
      axios.post('/search', { params })
        .then(({ data }) => {
          if (data.job_id !== undefined) {
            commit('updateJobID', data.job_id);
            setTimeout(() => dispatch('checkLoad'), 500);
          } else {
            commit('updateHits', data.entries);
            commit('updateCounts', data.aggregations);
            window.scrollTo(0, 0);
            const status = { loading: false, error: false, timestamp: new Date() };
            store.dispatch('utils/setStatus', status, { root: true });
          }
        });
    },
    upload({ commit }, params) {
      const formData = new FormData();
      if (params.type === 'file') {
        formData.append('file', params.value);
      } else if (params.type === 'url') {
        formData.append('url', params.value);
      }
      axios.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
        .then(({ data }) => {
          if (params.append) {
            data.entries.forEach(({ id, meta, path, preview }) => {
              const query = {
                type: 'idx',
                positive: true,
                value: id,
                weights: {},
                roi: null,
                label: meta.title,
                path,
                preview,
              };
              commit('addQuery', query);
            });
          } else {
            const queries = [];
            data.entries.forEach(({ id, meta, path, preview }) => {
              queries.push({
                type: 'idx',
                positive: true,
                value: id,
                weights: {},
                roi: null,
                label: meta.title,
                path,
                preview,
              });
            });
            commit('updateQuery', queries);
            commit('removeAllFilters');
          }
        });
    },
    async fetchIDXQuery(context, params) {
      let res;
      try {
        res = await axios.post(
          '/get',
          { params: { id: params.value } },
        );
      } catch (error) {
        return { ...params };
      }
      const title = [];
      const { preview } = res.data.entry;
      res.data.entry.meta.forEach(({ name, value_str }) => {
        if (name === 'title' && value_str) {
          title.push(value_str);
        }
      });
      if (!title.length) title.push('No title');
      return { ...params, label: title[0], preview };
    },
    async setState({ commit, dispatch }, params) {
      const queries = [];
      const filters = {};
      let lang = 'en';
      let fullText = [];
      let random = null;
      let dateRange = [];
      let count = 0;
      let maxCount = Object.keys(params).length;
      await new Promise((resolve) => {
        if (maxCount) {
          Object.keys(params).forEach((field) => {
            const values = params[field];
            try {
              switch (field) {
                case 'lang':
                  if (['en', 'EN'].includes(values)) {
                    lang = values.toLowerCase();
                  }
                  break;
                case 'query':
                  maxCount += values.split(',').length - 1;
                  values.split(',').forEach(async (value) => {
                    let positive = true;
                    let type = 'txt';
                    if (value.includes(':')) {
                      [type, value] = lsplit(value, ':', 1);
                      if (['+', '-'].includes(type.charAt(0))) {
                        if (type.charAt(0) === '-') {
                          positive = false;
                        }
                        type = type.slice(1);
                      }
                    }
                    let newQuery = { type, positive, value };
                    if (type === 'idx') {
                      newQuery = { ...newQuery, weights: {}, roi: null };
                      await dispatch('fetchIDXQuery', newQuery).then((result) => {
                        queries.push(result);
                        count += 1;
                        if (count === maxCount) {
                          resolve();
                        }
                      });
                    } else {
                      queries.push(newQuery);
                      count += 1;
                    }
                  });
                  break;
                case 'random':
                  random = values;
                  break;
                case 'period': {
                  const period = values.split('-').map(
                    (x) => parseInt(x, 10),
                  );
                  if (period.length === 1) {
                    period.push(period[0]);
                  } else if (period.length > 2) {
                    period.splice(-1, 9e9);
                  }
                  if (period[0] >= 1000 && period[1] <= 2000) {
                    dateRange = period;
                  }
                  break;
                }
                case 'full.text':
                  fullText = values.split(',');
                  break;
                default:
                  if (
                    config.DEFAULT_AGGREGATION_FIELDS.includes(field)
                    || field === 'collection'
                  ) {
                    values.split(',').forEach((name) => {
                      let positive = true;
                      if (['+', '-'].includes(name.charAt(0))) {
                        if (name.charAt(0) === '-') {
                          positive = false;
                        }
                        name = name.slice(1);
                      }
                      if (mixins.methods.keyInObj(field, filters)) {
                        if (field === 'collection') {
                          filters[field].push({ positive, hash_id: name });
                        } else {
                          filters[field].push({ positive, name });
                        }
                      } else if (field === 'collection') {
                        filters[field] = [{ positive, hash_id: name }];
                      } else {
                        filters[field] = [{ positive, name }];
                      }
                    });
                  }
              }
            } catch (error) {
              console.log(field, error);
            } finally {
              if (field !== 'query') {
                count += 1;
              }
              if (count === maxCount) {
                resolve();
              }
            }
          });
        } else {
          resolve();
        }
      });
      commit('updateLang', lang);
      commit('updateQuery', queries);
      commit('updateRandom', random);
      commit('updateFilters', filters);
      commit('updateFullText', fullText);
      commit('updateDateRange', dateRange);
      if (Object.keys(filters).length) {
        const update = { drawer: 'filter', value: true };
        commit('user/updateDrawer', update, { root: true });
      }
    },
    getState({ state }) {
      const params = new URLSearchParams();
      if (state.lang) {
        params.append('lang', state.lang);
      }
      if (state.query.length) {
        const query = state.query.map((v) => {
          let prefix = '+';
          if (!v.positive) prefix = '-';
          return `${prefix}${v.type}:${v.value}`;
        });
        params.append('query', query.join(','));
      }
      if (state.random) {
        params.append('random', state.random);
      }
      if (state.dateRange.length) {
        const period = state.dateRange.join('-');
        params.append('period', period);
      }
      if (state.fullText.length) {
        const fullText = state.fullText.join(',');
        params.append('full.text', fullText);
      }
      if (Object.keys(state.filters).length) {
        Object.keys(state.filters).forEach((field) => {
          if (state.filters[field].length) {
            const names = state.filters[field].map((n) => {
              let prefix = '+';
              if (!n.positive) prefix = '-';
              if (field === 'collection') {
                return `${prefix}${n.hash_id}`;
              }
              return `${prefix}${n.name}`;
            });
            params.append(field, names.join(','));
          }
        });
      }
      if (router.currentRoute.path === '/search') {
        const href = `?${params.toString()}`;
        window.history.pushState({}, null, href);
      } else {
        const query = Object.fromEntries(params);
        router.push({ path: 'search', query });
      }
    },
  },
  mutations: {
    updateJobID(state, jobID) {
      state.jobID = jobID;
    },
    updateHits(state, hits) {
      state.hits = hits;
    },
    updateCounts(state, counts) {
      state.counts = counts;
    },
    updateRandom(state, random) {
      if (typeof random === 'boolean') {
        if (random) {
          state.random = mixins.methods.getHash(new Date());
          state.query = [];
        } else {
          state.random = null;
        }
      } else if (typeof random === 'string') {
        state.random = random;
      }
    },
    updateSettings(state, settings) {
      state.settings = settings;
    },
    updateDateRange(state, dateRange) {
      state.dateRange = dateRange;
    },
    updateFullText(state, fullText) {
      state.fullText = fullText;
    },
    updateParams(state, params) {
      params = mixins.methods.stringify(params);
      state.prevParams = JSON.parse(params);
    },
    toggleBackBtn(state) {
      state.backBtn = !state.backBtn;
    },
    addQuery(state, query) {
      if (query) {
        const index = state.query.indexOf(query);
        if (index === -1) {
          state.query.push(query);
        }
      }
    },
    removeQuery(state, query) {
      const index = state.query.indexOf(query);
      if (index !== -1) {
        state.query.splice(index, 1);
      }
    },
    removeAllQueries(state) {
      if (state.query.length) {
        state.query = [];
      }
    },
    updateQuery(state, query) {
      if (!mixins.methods.isEqual(state.query, query)) {
        state.query = query;
      }
    },
    updateLang(state, lang) {
      state.lang = lang;
    },
    addFilter(state, { field, filter }) {
      if (mixins.methods.keyInObj(field, state.filters)) {
        if (!state.filters[field].includes(filter)) {
          state.filters[field].push(filter);
        }
      } else {
        Vue.set(state.filters, field, [filter]);
      }
    },
    removeAllFilters(state) {
      if (Object.keys(state.filters).length) {
        state.filters = {};
      }
      if (state.dateRange.length) {
        state.dateRange = [];
      }
      if (state.fullText.length) {
        state.fullText = [];
      }
      state.bookmarks = false;
    },
    updateFilters(state, filters) {
      if (!mixins.methods.isEqual(state.filters, filters)) {
        state.filters = filters;
      }
    },
    updateAll(state, params) {
      if (mixins.methods.keyInObj('query', params)) {
        state.query = params.query;
      }
      if (mixins.methods.keyInObj('random', params)) {
        state.random = params.random;
      }
      if (mixins.methods.keyInObj('filters', params)) {
        state.filters = params.filters;
      }
      if (mixins.methods.keyInObj('full_text', params)) {
        state.fullText = params.full_text;
      }
      if (mixins.methods.keyInObj('date_range', params)) {
        state.dateRange = params.date_range;
      }
    },
  },
};

export default api;
