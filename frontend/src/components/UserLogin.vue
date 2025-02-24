<template>
  <v-card
    max-width="450"
    flat
  >
    <v-card-title>
      {{ $t("user.login.title") }}

      <v-btn
        @click="close"
        absolute
        right
        icon
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text>
      <v-form v-model="isFormValid">
        <v-text-field
          v-model="user.name"
          :placeholder="$t('user.name')"
          prepend-icon="mdi-account"
          :rules="[checkLength]"
          tabindex="1"
          counter="75"
          clearable
        />

        <v-text-field
          v-model="user.password"
          :append-icon="
            showPassword ? 'mdi-eye-outline' : 'mdi-eye-off-outline'
          "
          :placeholder="$t('user.password')"
          prepend-icon="mdi-lock"
          @click:append="showPassword = !showPassword"
          :type="showPassword ? 'text' : 'password'"
          :rules="[checkLength]"
          tabindex="2"
          counter="75"
          clearable
        />
      </v-form>
    </v-card-text>

    <v-card-actions class="px-6 pb-6">
      <v-btn
        @click="login"
        :disabled="!isFormValid"
        tabindex="3"
        color="accent"
        depressed
        rounded
        block
      >
        {{ $t("user.login.title") }}
      </v-btn>

      <div
        class="grey--text pt-2"
        style="text-align: center"
      >
        {{ $t("user.login.text") }}

        <v-dialog
          v-model="dialog.register"
          max-width="400"
        >
          <template v-slot:activator="{ on }">
            <v-btn
              v-on="on"
              small
              text
            >
              {{ $t("user.register.title") }}
            </v-btn>
          </template>

          <UserRegister v-model="dialog.register" />
        </v-dialog>
      </div>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  props: {
    value: Boolean,
  },
  data() {
    return {
      showPassword: false,
      isFormValid: false,
      dialog: {
        register: false,
      },
      user: {},
    };
  },
  methods: {
    login() {
      this.$store.dispatch('user/login', this.user);
    },
    close() {
      this.$emit('input', false);
    },
    checkLength(value) {
      if (value) {
        if (value.length < 5) {
          return this.$tc('user.login.rules.min', 5);
        }
        if (value.length > 75) {
          return this.$tc('user.login.rules.max', 75);
        }
        return true;
      }
      return this.$t('field.required');
    },
  },
  computed: {
    status() {
      const { error, loading } = this.$store.state.utils.status;
      return !loading && !error;
    },
    timestamp() {
      return this.$store.state.utils.status.timestamp;
    },
  },
  watch: {
    'dialog.register'(value) {
      if (value) {
        this.close();
      }
    },
    timestamp() {
      if (this.status) {
        this.close();
        // TODO: reload
      }
    },
  },
  components: {
    UserRegister: () => import('@/components/UserRegister.vue'),
  },
};
</script>

<style scoped>
.v-card__actions {
  display: block;
}
</style>
