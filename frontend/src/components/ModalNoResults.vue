<template>
  <v-dialog
    v-model="dialog"
    max-width="450px"
  >
    <v-card>
      <v-card-title class="mb-2">
        {{ $t("modal.noresults.title") }}

        <v-btn icon @click.native="dialog=false" absolute top right>
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <div class="mb-4">{{ $t("modal.noresults.text") }}</div>

        <v-btn color="primary" width="50%" plain @click="removeAllFilters">
          {{ $t("drawer.filter.remove") }}
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
  props: ['entries'],
  data() {
    return {
      dialog: false,
    };
  },
  methods: {
    removeAllFilters() {
      this.$store.commit('api/removeAllFilters');
      this.dialog = false;
    },
  },
  watch: {
    entries(value) {
      if (typeof value !== 'undefined') {
        if (value.length === 0) {
          this.dialog = true;
        } else {
          this.dialog = false;
        }
      }
    },
  },
};
</script>
