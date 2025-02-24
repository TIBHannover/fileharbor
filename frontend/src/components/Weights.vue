<template>
  <v-card
    :id="id"
    class="weights"
    width="300"
  >
    <v-card-text class="mb-n4">
      <v-switch
        v-if="local"
        v-model="selectWeights"
        class="mt-0 mx-2"
        :label="$t('modal.weights.toggle')"
        color="secondary"
        inset
        hide-details
      ></v-switch>

      <div
        v-if="selectWeights"
        :class="local ? 'mt-6 mb-n4' : 'mb-n4'"
      >
        <div
          v-for="(values, key, index) in weights"
          :key="index"
          :title="weights[key].name"
          class="weight mb-4"
        >
          <v-slider
            v-model="weights[key].value"
            min="0.0"
            max="1.0"
            step="0.01"
            color="secondary"
            :prepend-icon="weights[key].icon"
            @end="check(key)"
            hide-details
          >
            <template v-slot:append>
              <v-text-field
                v-model="weights[key].value"
                type="number"
                class="mt-0 pt-0"
                background-color="grey lighten-4"
                style="width: 80px"
                @change="check(key)"
                hide-details
                single-line
                rounded
                flat
              ></v-text-field>

              <v-btn
                v-if="weights[key].advanced"
                @click="weights[key].advanced = false"
                :title="$t('modal.weights.advanced.hide')"
                class="ml-2"
                icon
                small
              >
                <v-icon>mdi-cog-off-outline</v-icon>
              </v-btn>
              <v-btn
                v-else
                :title="$t('modal.weights.advanced.show')"
                @click="weights[key].advanced = true"
                class="ml-2"
                :disabled="weights[key].items.length < 2"
                icon
                small
              >
                <v-icon>mdi-cog-outline</v-icon>
              </v-btn>
            </template>
          </v-slider>

          <v-select
            v-if="weights[key].items.length > 1 && weights[key].advanced"
            v-model="weights[key].default"
            :items="weights[key].items"
            @change="update"
            item-value="key"
            item-text="name"
            style="font-size: 14px"
            class="ml-10"
            :attach="'#' + id"
            solo
            hide-details
            flat
            dense
          >
            <template v-slot:prepend>
              <span>{{ $t("field.use") }}</span>
            </template>
          </v-select>
        </div>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  data() {
    return {
      id: `w${String(Math.round(Math.random() * 1000))}`,
      selectWeights: false,
      weights: {
        color: {
          default: 'yuv_histogram_feature',
          icon: 'mdi-palette-outline',
          name: this.$t('modal.weights.group.color'),
          advanced: false,
          value: 0.0,
          items: [
            { key: 'yuv_histogram_feature', name: 'YUV Histogram' },
          ],
        },
        content: {
          default: 'clip_embedding_feature',
          icon: 'mdi-image-outline',
          name: this.$t('modal.weights.group.content'),
          advanced: false,
          value: 1.0,
          items: [
            { key: 'clip_embedding_feature', name: 'CLIP Embedding' },
            { key: 'byol_embedding_feature', name: 'Wikimedia Embedding' },
            { key: 'image_net_inception_feature', name: 'ImageNet Embedding' },
          ],
        },
      },
    };
  },
  props: {
    value: Object,
    local: Boolean,
  },
  methods: {
    check(key) {
      const total = Object.values(this.weights).reduce(
        (t, weight) => t + weight.value,
        0,
      );
      if (total === 0) {
        this.weights[key].value = 0.5;
      }
      this.update();
    },
    update() {
      const weights = {};
      if (this.selectWeights) {
        Object.values(this.weights).forEach((weight) => {
          weight.items.forEach((item) => {
            if (item.key === weight.default && weight.value > 0) {
              weights[item.key] = weight.value;
            }
          });
        });
      }
      if (Object.keys(weights).length) {
        this.$emit('update', weights);
      }
    },
    change() {
      if (this.value && Object.keys(this.value).length) {
        Object.keys(this.weights).forEach((group) => {
          const keys = this.weights[group].items.map((x) => x.key);
          Object.keys(this.value).every((key) => {
            if (this.value[key] > 0 && keys.includes(key)) {
              this.weights[group].default = key;
              this.weights[group].value = this.value[key];
              return false;
            }
            return true;
          });
        });
      } else {
        this.weights.color.default = 'yuv_histogram_feature';
        this.weights.color.value = 0.0;
        this.weights.content.default = 'clip_embedding_feature';
        this.weights.content.value = 1.0;
      }
      this.update();
    },
  },
  computed: {
    reset() {
      return this.$store.state.api.settings.weights;
    },
  },
  watch: {
    reset(newValues, oldValues) {
      if (!this.local && !this.isEqual(newValues, oldValues)) {
        this.change();
      }
    },
  },
  created() {
    this.change();
    if (!this.local || (this.value && Object.keys(this.value).length)) {
      this.selectWeights = true;
    }
  },
};
</script>

<style scoped>
.weight .row > label {
  align-items: center;
}

.weight .v-select .v-input__slot {
  padding-right: 3px !important;
  padding-left: 1px !important;
}

.weight .v-select .v-input__prepend-outer {
  margin: 5px 4px 3px 0 !important;
  align-items: center;
  height: 30px;
}

.weights.v-sheet.v-card:not(.v-sheet--outlined) {
  box-shadow: none;
}
</style>
