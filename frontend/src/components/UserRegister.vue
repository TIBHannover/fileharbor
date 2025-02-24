<template>
  <v-card
    max-width="450"
    flat
  >
    <v-card-title>
      {{ $t("user.register.title") }}

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
          v-model="user.email"
          :placeholder="$t('user.email')"
          prepend-icon="mdi-email"
          :rules="[checkLength]"
          tabindex="2"
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
          tabindex="3"
          counter="75"
          clearable
        />
      </v-form>
    </v-card-text>

    <v-card-actions class="px-6 pb-6">
      <v-btn
        @click="register"
        :disabled="!isFormValid"
        tabindex="4"
        color="accent"
        depressed
        rounded
        block
      >
        {{ $t("user.register.title") }}
      </v-btn>
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
      user: {},
      isFormValid: false,
      showPassword: false,
    };
  },
  methods: {
    register() {
      this.$store.dispatch('user/register', this.user);
    },
    close() {
      this.$emit('input', false);
    },
    checkLength(value) {
      if (value) {
        if (value.length < 5) {
          return this.$tc('user.register.rules.min', 5);
        }
        if (value.length > 75) {
          return this.$tc('user.register.rules.max', 75);
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
    timestamp() {
      if (this.status) {
        this.close();
      }
    },
  },
};
</script>
