<template>
  <v-btn
    :title="$t('help.title')"
    @click="help"
    class="help"
    color="accent"
    fixed
    fab
    large
    bottom
    right
  >
    <v-icon>mdi-help</v-icon>
  </v-btn>
</template>

<script>
export default {
  data() {
    return {
      options: {
        disableInteraction: true,
        keyboardNavigation: true,
      },
    };
  },
  methods: {
    help() {
      const { path } = this.$router.currentRoute;
      this.$store.commit('user/updateAllDrawers', true);
      let startStep = 1;
      const steps = [
        {
          intro: this.$t('help.search.general'),
          element: '#search-general',
          ...this.options,
        },
        {
          intro: this.$t('help.search.image'),
          element: '#search-image',
          ...this.options,
        },
        {
          intro: this.$t('help.search.random'),
          element: '#search-random',
          ...this.options,
        },
      ];
      if (path === '/search') {
        steps.push(...[
          {
            intro: this.$t('help.filter.general'),
            element: '#filter-general',
            ...this.options,
          },
          {
            intro: this.$t('help.filter.period'),
            element: '.v-navigation-drawer .date-range',
            ...this.options,
          },
          {
            intro: this.$t('help.settings.general'),
            element: '#settings-general',
            ...this.options,
          },
          {
            intro: this.$t('help.settings.weights'),
            element: '#weights-col',
            tooltipClass: 'move-right',
            position: 'right',
            ...this.options,
          },
          {
            intro: this.$t('help.settings.layout'),
            element: '#layout-col',
            tooltipClass: 'move-right',
            position: 'right',
            ...this.options,
          },
          {
            intro: this.$t('help.settings.cluster'),
            element: '#cluster-col',
            position: 'left',
            ...this.options,
          },
        ]);
        if (this.isClusterView) {
          if (this.is2dView) {
            steps.push({
              intro: this.$t('help.cluster.2d'),
              ...this.options,
            });
          } else {
            steps.push({
              intro: this.$t('help.cluster.1d'),
              ...this.options,
            });
          }
          startStep = steps.length;
        }
      }
      window.scrollTo(0, 0);
      this.$intro().addSteps(steps)
        .onbeforechange((el) => {
          let modal = { modal: null, value: false };
          this.$store.commit('user/updateAllModals', false);
          if (el) {
            switch (el.id) {
              case 'weights-col':
                modal = { modal: 'weights', value: true };
                this.$store.commit('user/updateModal', modal);
                break;
              case 'layout-col':
                modal = { modal: 'layout', value: true };
                this.$store.commit('user/updateModal', modal);
                break;
              case 'cluster-col':
                modal = { modal: 'cluster', value: true };
                this.$store.commit('user/updateModal', modal);
                break;
              default:
                break;
            }
          }
        })
        .onexit(() => {
          this.$store.commit('user/updateAllModals', false);
        })
        .start()
        .goToStep(startStep);
    },
  },
  computed: {
    isClusterView() {
      const { settings } = this.$store.state.api;
      if (
        this.keyInObj('n', settings.cluster)
        && settings.cluster.n > 1
      ) {
        return true;
      }
      return false;
    },
    is2dView() {
      const { settings } = this.$store.state.api;
      if (
        this.keyInObj('viewType', settings.layout)
        && settings.layout.viewType === 'umap'
      ) {
        return true;
      }
      return false;
    },
  },
};
</script>

<style>
.help.v-btn {
  z-index: 99;
}

.help.v-btn--fab.v-size--large.v-btn--absolute.v-btn--bottom {
  bottom: 0;
}
</style>
