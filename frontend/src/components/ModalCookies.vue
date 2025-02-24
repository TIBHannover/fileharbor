<template>
  <v-dialog
    v-model="dialog"
    max-width="450px"
    persistent
  >
    <v-card>
      <v-card-title class="mb-2">
        {{ $t("modal.cookies.title") }}
      </v-card-title>

      <v-card-text>
        <div class="mb-4">{{ $t("modal.cookies.text") }}</div>

        <v-btn color="primary" width="50%" plain @click="dialog=false">
          {{ $t("button.accept") }}
        </v-btn>
        <v-btn color="grey" width="50%" plain @click="dialog=false">
          {{ $t("button.cancel") }}
        </v-btn>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
    };
  },
  created() {
    const { csrfToken } = this.$store.state.user;
    if (csrfToken !== null) this.dialog = false;
  },
};
</script>
