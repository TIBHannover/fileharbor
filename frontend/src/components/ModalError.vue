<template>
  <v-dialog
    v-model="dialog"
    max-width="450px"
  >
    <v-card>
      <v-card-title class="mb-2">
        {{ $t("modal.error.title") }}

        <v-btn
          @click.native="dialog = false"
          absolute
          right
          icon
          top
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <p>
          <span
            v-for="detail in details"
            :key="detail"
          >
            {{ keyInObj(detail, $t("modal.error.detail")) ? $t("modal.error.detail")[detail] : $t("modal.error.detail.unknown_error") }}
          </span>
        </p>

        <v-btn
          @click="reload"
          color="primary"
          width="50%"
          plain
        >
          {{ $t("button.reload") }}
        </v-btn>

        <v-btn
          @click="dialog = false"
          color="grey"
          width="50%"
          plain
        >
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
  methods: {
    reload() {
      window.location.reload();
      this.dialog = false;
    },
  },
  computed: {
    timestamp() {
      return this.$store.state.utils.message.timestamp;
    },
    details() {
      return this.$store.state.utils.message.details;
    },
  },
  watch: {
    timestamp() {
      this.dialog = true;
    },
  },
};
</script>
