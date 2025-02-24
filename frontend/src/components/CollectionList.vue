<template>
  <v-card>
    <v-card-title class="mb-2">
      {{ $t("modal.collection.list.title") }}

      <v-btn
        @click.native="close"
        absolute
        right
        icon
        top
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text>
      <v-data-table
        :headers="headers"
        :footer-props="footerProps"
        :items="data"
        hide-default-footer
        multi-sort
      >
        <template v-slot:item.status="{ item }">
          <v-progress-circular
            v-if="item.status === 'U'"
            :title="item.progress + '%'"
            indeterminate
            color="primary"
            width="1.25"
            size="15"
          />

          <v-icon
            v-if="item.status === 'R'"
            style="font-size: 20px;"
          >
            mdi-check-circle-outline
          </v-icon>

          <v-icon
            v-if="item.status === 'E'"
            style="font-size: 20px;"
            color="accent"
          >
            mdi-alert-circle-outline
          </v-icon>
        </template>

        <template v-slot:item.date="{ item }">
          {{ toDate(item.date) }}
        </template>

        <template v-slot:item.actions="{ item }">
          <v-icon
            @click="showCollection(item)"
            :title="$t('button.show')"
            class="mr-2"
            small
           >
            mdi-eye-outline
          </v-icon>

          <v-icon
            @click="deleteCollection(item)"
            :title="$t('button.delete')"
            small
          >
            mdi-trash-can-outline
          </v-icon>
        </template>
      </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  props: {
    value: Boolean,
  },
  data() {
    return {
      checkInterval: null,
      headers: [
        { text: '', value: 'status', width: 10, sortable: false },
        { text: this.$t('modal.collection.list.table.name'), value: 'name' },
        { text: this.$t('modal.collection.list.table.count'), value: 'count', align: 'end', width: 150 },
        { text: this.$t('modal.collection.list.table.date'), value: 'date', align: 'end', width: 150 },
        { text: this.$t('modal.collection.list.table.actions'), value: 'actions', align: 'end', width: 100, sortable: false },
      ],
      footerProps: {
        'items-per-page-text': '',
      },
    };
  },
  methods: {
    close() {
      this.$emit('input', false);
    },
    toDate(item) {
      return new Date(item).toLocaleDateString();
    },
    showCollection(item) {
      const { hash_id, name } = item;
      const filter = { positive: true, hash_id, name };
      this.$store.commit('api/updateFilters', { collection: [filter] });
      this.close();
    },
    deleteCollection(item) {
      this.$store.dispatch('collection/delete', item);
    },
  },
  computed: {
    data() {
      return this.$store.state.collection.collections;
    },
  },
  watch: {
    data() {
      clearInterval(this.checkInterval);
      if (this.value) {
        this.checkInterval = setInterval(() => {
          this.$store.dispatch('collection/list');
        }, 5000);
      }
    },
    value(visible) {
      if (visible) {
        this.$store.dispatch('collection/list');
      }
    },
  },
};
</script>

<style scoped>
.v-data-footer__select > div {
  display: none;
}
</style>
