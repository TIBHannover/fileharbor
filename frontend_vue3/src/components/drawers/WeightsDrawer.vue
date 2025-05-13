<script setup>
import { ref, watch, computed, defineModel } from 'vue'
import { storeToRefs } from 'pinia'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

const model = defineModel()

const visualWeight = ref(50)
const textualWeight = ref(50)

const weights = ref({
  color: {
    default: 'yuv_histogram_feature',
    icon: 'mdi-palette-outline',
    name: t('modal.weights.group.color'),
    advanced: false,
    value: 0.0,
    items: [{ key: 'yuv_histogram_feature', name: 'YUV Histogram' }],
  },
  content: {
    default: 'clip_embedding_feature',
    icon: 'mdi-image-outline',
    name: t('modal.weights.group.content'),
    advanced: false,
    value: 0.5,
    items: [
      { key: 'clip_embedding_feature', name: 'CLIP Embedding' },
      { key: 'byol_embedding_feature', name: 'Wikimedia Embedding' },
      { key: 'image_net_inception_feature', name: 'ImageNet Embedding' },
    ],
  },
  meta: {
    default: 'clip_embedding_feature',
    icon: 'mdi-text-box-outline',
    name: t('modal.weights.group.meta'),
    advanced: false,
    value: 0.5,
    items: [{ key: 'clip_embedding_feature', name: 'CLIP Embedding' }],
  },
})

function check(key) {
  const total = Object.values(weights.value).reduce((t, weight) => t + weight.value, 0)
  if (total === 0) {
    this.weights[key].value = 0.5
  }
}
</script>

<template>
  <v-navigation-drawer v-model="model">
    <div class="drawer">
      <div v-for="(values, key, index) in weights" :key="index" :title="weights[key].name">
        <div class="text-caption">{{ weights[key].name }}</div>
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
              variant="solo-filled"
              class="mt-0 pt-0"
              background-color="grey lighten-4"
              style="width: 80px"
              @change="check(key)"
              hide-details
              hide-spin-buttons
              flat
            ></v-text-field>
          </template>
        </v-slider>
      </div>
    </div>
  </v-navigation-drawer>
</template>

<style scoped>
.drawer {
  margin: 5px;
}
</style>
