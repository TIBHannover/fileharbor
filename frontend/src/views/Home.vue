<template>
  <v-app>
    <v-app-bar
      color="white"
      app
      flat
    >
      <v-layout
        class="mx-n2"
        justify-end
      >
        <History />
        <UserMenu />
      </v-layout>
    </v-app-bar>

    <v-main>
      <v-layout
        style="height: 100%"
        justify-center
        align-center
      >
        <v-col cols="6">
          <v-row
            class="mb-10"
            justify="center"
          >
            <div class="logo">
              <img :title="appName" src="/assets/images/logo.png" />
            </div>
          </v-row>

          <v-row class="mb-4">
            <SearchBar />
          </v-row>
        </v-col>
      </v-layout>
    </v-main>

    <HelpButton />
    <Footer />
  </v-app>
</template>

<script>
export default {
  data() {
    return {
      appName: process.env.VUE_APP_NAME,
    };
  },
  methods: {
    load() {
      this.$store.dispatch('api/load');
    },
  },
  computed: {
    filters() {
      return this.$store.state.api.filters;
    },
  },
  watch: {
    filters: {
      handler() {
        this.load();
      },
      deep: true,
    },
  },
  components: {
    Footer: () => import('@/components/Footer.vue'),
    History: () => import('@/components/History.vue'),
    UserMenu: () => import('@/components/UserMenu.vue'),
    SearchBar: () => import('@/components/SearchBar.vue'),
    HelpButton: () => import('@/components/HelpButton.vue'),
  },
};
</script>

<style scoped>
.logo > img {
  max-height: 56px;
}
</style>
