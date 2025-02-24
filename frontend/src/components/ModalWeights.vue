<template>
  <v-menu
    v-model="dialog"
    :close-on-content-click="false"
    min-width="300"
    max-width="300"
    offset-y
    bottom
    right
    open-on-hover
  >
    <template v-slot:activator="{ on }">
      <v-btn
        v-on="on"
        text
        block
      >
        <v-icon
          color="grey darken-1"
          class="mr-2 ml-n1"
        >
          mdi-compass-outline
        </v-icon>
        <v-badge
          v-if="changed"
          color="accent"
          dot
        >
          <span style="font-size: 14px">
            {{ $t("modal.weights.title") }}
          </span>
        </v-badge>
        <span
          v-else
          style="font-size: 14px"
        >
          {{ $t("modal.weights.title") }}
        </span>
      </v-btn>
    </template>

    <Weights
      v-model="weights"
      :local="false"
      @update="update"
    />

    <div class="pa-6">
      <v-btn
        @click="submit"
        color="accent"
        block
        rounded
        depressed
      >
        {{ $t("button.update") }}
      </v-btn>
    </div>
  </v-menu>
</template>

<script>
import Weights from '@/components/Weights.vue';

export default {
  data() {
    return {
      weights: this.values,
      dialog: false,
    };
  },
  props: ['values'],
  methods: {
    submit() {
      this.$emit('update', this.weights);
    },
    update(values) {
      this.weights = values;
    },
  },
  computed: {
    toggle() {
      return this.$store.state.user.modal.weights;
    },
    changed() {
      if (this.values && Object.keys(this.values).length) {
        const defaultValue = { clip_embedding_feature: 1 };
        return !this.isEqual(this.values, defaultValue);
      }
      return false;
    },
  },
  watch: {
    toggle(value) {
      this.dialog = value;
    },
  },
  components: {
    Weights,
  },
};
</script>
