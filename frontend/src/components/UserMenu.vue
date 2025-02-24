<template>
  <v-menu
    v-model="menu"
    min-width="175"
    open-on-hover
    offset-y
    bottom
    left
    close-delay="100"
    close-on-click="false"
    close-on-content-click="false"
  >
    <template v-slot:activator="{ attrs, on }">
      <v-btn
        :title="$t('user.menu.title')"
        v-bind="attrs"
        v-on="on"
        class="ml-n2"
        icon
      >
        <v-badge v-if="loggedIn" color="accent" dot>
          <v-icon color="primary">mdi-account-circle</v-icon>
        </v-badge>

        <v-icon v-else color="primary"> mdi-account-circle </v-icon>
      </v-btn>
    </template>

    <UserAccount v-if="loggedIn" />

    <v-list v-if="loggedIn" class="pa-0">
      <v-list-item-group>
        <v-dialog v-model="dialog.upload" max-width="400">
          <template v-slot:activator="{ on }">
            <v-list-item v-on="on">
              {{ $t("modal.collection.upload.title") }}
            </v-list-item>
          </template>

          <CollectionUpload v-model="dialog.upload" />
        </v-dialog>

        <v-dialog v-model="dialog.list" max-width="800">
          <template v-slot:activator="{ on }">
            <v-list-item v-if="collections.length" v-on="on">
              <v-badge :content="collections.length" color="accent" inline>
                {{ $t("modal.collection.list.title") }}
              </v-badge>
            </v-list-item>
          </template>

          <CollectionList v-model="dialog.list" />
        </v-dialog>
      </v-list-item-group>
    </v-list>

    <v-list v-else class="pa-0">
      <v-list-item-group>
        <v-dialog v-model="dialog.login" max-width="400">
          <template v-slot:activator="{ on }">
            <v-list-item v-on="on">
              {{ $t("user.login.title") }}
            </v-list-item>
          </template>

          <UserLogin v-model="dialog.login" />
        </v-dialog>

        <v-dialog v-model="dialog.register" max-width="400">
          <template v-slot:activator="{ on }">
            <v-list-item v-on="on">
              {{ $t("user.register.title") }}
            </v-list-item>
          </template>

          <UserRegister v-model="dialog.register" />
        </v-dialog>
      </v-list-item-group>
    </v-list>
  </v-menu>
</template>

<script>
export default {
  data() {
    return {
      menu: false,
      dialog: {
        list: false,
        login: false,
        upload: false,
        register: false,
      },
    };
  },
  methods: {
    close() {
      this.menu = false;
    },
  },
  computed: {
    loggedIn() {
      return this.$store.state.user.loggedIn;
    },
    collections() {
      return this.$store.state.collection.collections;
    },
    toggleList() {
      return this.$store.state.collection.modal.list;
    },
  },
  watch: {
    dialog: {
      handler(dialogs) {
        Object.values(dialogs).forEach((visible) => {
          if (visible) {
            this.close();
          }
        });
      },
      deep: true,
    },
    toggleList(value) {
      this.dialog.list = value;
    },
  },
  components: {
    UserLogin: () => import("@/components/UserLogin.vue"),
    UserAccount: () => import("@/components/UserAccount.vue"),
    UserRegister: () => import("@/components/UserRegister.vue"),
    CollectionList: () => import("@/components/CollectionList.vue"),
    CollectionUpload: () => import("@/components/CollectionUpload.vue"),
  },
};
</script>
