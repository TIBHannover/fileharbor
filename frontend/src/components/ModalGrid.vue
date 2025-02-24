<template>
  <v-dialog :value="value" @input="$emit('input')" max-width="750px">
    <v-card>
      <v-card-title>
        <div class="text-h6">
          {{ $t("modal.grid.title") }}
        </div>

        <v-btn icon @click.native="$emit('input')" absolute top right>
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="mt-4">
        <GridCluster v-if="layout==='cluster'" :entries="entries" />
        <GridRanked v-if="layout==='ranked'" :entries="entries" />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import GridRanked from '@/components/GridRanked.vue';
import GridCluster from '@/components/GridCluster.vue';

export default {
  props: ['value', 'entries'],
  computed: {
    layout() {
      const { settings } = this.$store.state.api;
      if (
        this.keyInObj('n', settings.cluster)
        && settings.cluster.n > 1
      ) {
        return 'cluster';
      }
      return 'ranked';
    },
  },
  components: {
    GridRanked,
    GridCluster,
  },
};
</script>
