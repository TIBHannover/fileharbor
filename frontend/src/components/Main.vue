<template>
  <v-main class="ma-1">
    <div
      v-if="entries"
      style="height: 100%;"
    >
      <Umap
        v-if="view === 'umap'"
        :data="entries"
      />
      <GridCluster
        v-if="view === 'cluster'"
        :entries="entries"
      />
      <GridRanked
        v-if="view === 'ranked'"
        :entries="entries"
      />
    </div>

    <Loader :updating="$asyncComputed.entries" />
    <ModalNoResults :entries="entries" />
  </v-main>
</template>

<script>
export default {
  data() {
    return {
      view: null,
    };
  },
  methods: {
    changeView() {
      if (this.viewType === 'umap') {
        this.view = 'umap';
      } else {
        const { cluster } = this.settings;
        if (cluster.n > 1) {
          this.view = 'cluster';
        } else {
          this.view = 'ranked';
        }
      }
    }
  },
  asyncComputed: {
    entries() {
      let data = this.data;
      const { sortType, sortOrder } = this.layout;
      if (data) {
        switch (sortType) {
          case 'title':
            data = data.map((entry) => {
              entry.order = 'zzzz';
              entry.meta.every(({ name, value_str }) => {
                if (name === 'title' && value_str) {
                  entry.order = value_str;
                  return false;
                }
                return true;
              });
              return entry;
            });
            data.sort((a, b) => a.order.localeCompare(b.order));
            break;
          case 'date':
            data = data.map((entry) => {
              entry.order = 9999;
              entry.meta.every(({ name, value_str }) => {
                if (name === 'year_min' && value_str) {
                  entry.order = value_str;
                  return false;
                }
                return true;
              });
              return entry;
            });
            data.sort((a, b) => a.order - b.order);
            break;
          default:
            break;
        }
        if (sortOrder === 'desc') {
          data = [...data].reverse();
        }
      }
      return new Promise((resolve) => setTimeout(() => resolve(data), 5));
    },
  },
  computed: {
    data() {
      return this.$store.state.api.hits;
    },
    settings() {
      return this.$store.state.api.settings;
    },
    layout() {
      return this.settings.layout;
    },
    viewType() {
      return this.layout.viewType;
    },
  },
  watch: {
    entries() {
      this.$nextTick(() => {
        this.changeView();
      });
    },
    viewType() {
      this.changeView();
    },
  },
  components: {
    Umap: () => import('@/components/Umap2D.vue'),
    Loader: () => import('@/components/Loader.vue'),
    GridRanked: () => import('@/components/GridRanked.vue'),
    GridCluster: () => import('@/components/GridCluster.vue'),
    ModalNoResults: () => import('@/components/ModalNoResults.vue'),
  },
};
</script>
