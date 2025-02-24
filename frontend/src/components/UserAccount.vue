<template>
  <v-list-item-content class="account justify-center pa-10">
    <div class="mx-auto text-center">
      <v-avatar color="secondary">
        <span class="white--text text-h5">{{ initials }}</span>
      </v-avatar>

      <h3 class="mt-5">{{ data.username }}</h3>

      <p
        class="text-caption clip mt-2 mb-0"
        style="max-width: 170px;"
      >
        {{ data.email }}
      </p>

      <p class="text-caption mb-0">
        <i>{{ joined }}</i>
      </p>
    </div>

    <div class="v-btn--absolute v-btn--right v-btn--top">
      <v-btn
        :title="$t('user.logout.title')"
        class="mr-n2 mt-n2"
        @click="logout"
        icon
      >
        <v-icon>mdi-logout-variant</v-icon>
      </v-btn>
    </div>
  </v-list-item-content>
</template>

<script>
export default {
  methods: {
    logout() {
      this.$store.dispatch('user/logout').then(() => {
        this.$store.commit('api/removeAllFilters');
        this.$store.commit('api/removeAllQueries');
      });
    },
  },
  computed: {
    data() {
      return this.$store.state.user.userData;
    },
    nDays() {
      const date = new Date(this.data.date);
      const diffInMs = new Date() - date;
      return Math.round(diffInMs / (1000 * 60 * 60 * 24));
    },
    joined() {
      return this.$tc('user.menu.joined', this.nDays || 0);
    },
    initials() {
      return this.data.username.slice(0, 2);
    },
  },
};
</script>

<style>
.v-list-item__content.account {
  min-width: 250px;
  letter-spacing: .0892857143em;
  border-bottom: 1px solid #f5f5f5;
}

.v-menu__content .account .v-btn:not(.accent) {
  justify-content: center;
}

.v-application .v-avatar.secondary {
  background-color: rgba(69,123,157,.54) !important;
  border-color: rgba(69,123,157,.54) !important;
}
</style>
