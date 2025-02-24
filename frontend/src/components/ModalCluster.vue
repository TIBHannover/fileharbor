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
          mdi-select-group
        </v-icon>
        <v-badge
          v-if="nClusters > 1"
          color="accent"
          :content="nClusters"
        >
          <span style="font-size: 14px">
            {{ $t("modal.cluster.title") }}
          </span>
        </v-badge>
        <span
          v-else
          style="font-size: 14px"
        >
          {{ $t("modal.cluster.title") }}
        </span>
      </v-btn>
    </template>

    <v-card
      id="cluster"
      width="300"
    >
      <v-card-text class="px-6 pt-4 pb-5">
        <v-select
          v-model="cluster.default"
          :items="cluster.items"
          class="mb-2"
          item-value="key"
          item-text="name"
          attach="#cluster"
          solo
          flat
          dense
          hide-details
          @change="update"
        >
          <template v-slot:prepend>
            {{ $t("field.use") }}
          </template>

          <template v-slot:append-outer>
            <v-btn
              v-if="cluster.highlight"
              class="ml-2"
              @click="changeClusterHighlight(false)"
              :title="$t('modal.cluster.method.highlight.hide')"
              :disabled="!is2dView"
              icon
              small
            >
              <v-icon>mdi-eye-off-outline</v-icon>
            </v-btn>
            <v-btn
              v-else
              class="ml-2"
              @click="changeClusterHighlight(true)"
              :title="$t('modal.cluster.method.highlight.show')"
              :disabled="!is2dView"
              icon
              small
            >
              <v-icon>mdi-eye-outline</v-icon>
            </v-btn>
          </template>
        </v-select>

        <div :title="$t('modal.cluster.n')">
          <v-slider
            v-model="nClusters"
            min="1"
            max="12"
            color="secondary"
            prepend-icon="mdi-format-list-numbered"
            hide-details
            @end="update"
          >
            <template v-slot:append>
              <v-text-field
                v-model="nClusters"
                type="number"
                class="mt-0 pt-0"
                background-color="grey lighten-4"
                style="width: 80px"
                hide-details
                single-line
                rounded
                flat
              ></v-text-field>
            </template>
          </v-slider>
        </div>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
export default {
  data() {
    return {
      dialog: false,
      nClusters: 1,
      cluster: {
        default: 'kmeans',
        highlight: true,
        items: [
          { key: 'kmeans', name: this.$t('modal.cluster.method.type.kmeans') },
          { key: 'gm', name: this.$t('modal.cluster.method.type.gm') },
          // { key: 'agglomerative', name: this.$t('modal.cluster.method.type.agglomerative') },
        ],
      },
    };
  },
  props: ['values'],
  methods: {
    update() {
      const values = {
        highlight: this.cluster.highlight,
        type: this.cluster.default,
        n: this.nClusters,
      };
      this.$emit('update', values);
    },
    change() {
      if (this.values && Object.keys(this.values).length) {
        if (this.keyInObj('highlight', this.values)) {
          this.cluster.highlight = this.values.highlight;
        }
        if (this.keyInObj('type', this.values)) {
          this.cluster.default = this.values.type;
        }
        if (this.keyInObj('n', this.values)) {
          this.nClusters = this.values.n;
        }
      } else {
        this.cluster.highlight = true;
        this.cluster.default = 'kmeans';
        this.nClusters = 1;
      }
      this.update();
    },
    changeClusterHighlight(value) {
      this.cluster.highlight = value;
      this.update();
    },
  },
  computed: {
    toggle() {
      return this.$store.state.user.modal.cluster;
    },
    reset() {
      return this.$store.state.api.settings.cluster;
    },
    is2dView() {
      const { settings } = this.$store.state.api;
      if (
        this.keyInObj('viewType', settings.layout)
        && settings.layout.viewType === 'umap'
      ) {
        return true;
      }
      return false;
    },
  },
  watch: {
    toggle(value) {
      this.dialog = value;
    },
    reset(newValues, oldValues) {
      if (!this.isEqual(newValues, oldValues)) {
        this.change();
      }
    },
    is2dView(value) {
      if (!value) {
        this.cluster.highlight = true;
      }
    },
  },
  created() {
    this.change();
  },
};
</script>

<style>
#cluster .v-select .v-input__slot {
  padding-right: 3px !important;
  padding-left: 1px !important;
}

#cluster .v-select .v-input__prepend-outer {
  display: flex;
  min-height: 27px;
  margin-right: 4px;
  align-items: center;
}
</style>
