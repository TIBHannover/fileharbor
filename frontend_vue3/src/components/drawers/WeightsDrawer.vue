<script setup>
import { ref, defineModel } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSearchStore } from '@/stores/search'
const { t } = useI18n()

const model = defineModel()

const searchStore = useSearchStore()

const weights = ref({
  color: {
    default: 'yuv_histogram_feature',
    icon: 'mdi-palette-outline',
    name: t('modal.weights.group.color'),
    advanced: false,
    value: 0.0,
    items: [{ key: 'yuv_histogram', name: 'YUV Histogram' }],
  },
  content: {
    default: 'clip_image',
    icon: 'mdi-image-outline',
    name: t('modal.weights.group.content'),
    advanced: false,
    value: 0.5,
    items: [
      { key: 'clip_image', name: 'CLIP Embedding' },
      { key: 'byol_wikimedia', name: 'Wikimedia Embedding' },
      { key: 'imagenet_inception', name: 'ImageNet Embedding' },
    ],
  },
  meta: {
    default: 'clip_text',
    icon: 'mdi-text-box-outline',
    name: t('modal.weights.group.meta'),
    advanced: false,
    value: 0.5,
    items: [{ key: 'clip_text', name: 'CLIP Embedding' }],
  },
})

function check(key) {
  const total = Object.values(weights.value).reduce((t, weight) => t + weight.value, 0)
  if (total === 0) {
    this.weights[key].value = 0.5
  }
}

function update() {
  let newWeights = []
  Object.values(weights.value).forEach((element) => {
    console.log(element.value)
    newWeights.push({ name: element.default, value: element.value })
  })
  searchStore.setGlobalWeights(newWeights)
  searchStore.search()
}
</script>

<template>
  <v-navigation-drawer v-model="model">
    <div class="drawer">
      <div
        v-for="(values, key, index) in weights"
        :key="index"
        :title="weights[key].name"
      >
        <div class="text-caption">
          {{ weights[key].name }}
        </div>
        <v-slider
          v-model="weights[key].value"
          min="0.0"
          max="1.0"
          step="0.01"
          color="secondary"
          :prepend-icon="weights[key].icon"
          hide-details
          @end="check(key)"
        >
          <template #append>
            <v-text-field
              v-model="weights[key].value"
              type="number"
              variant="solo-filled"
              class="mt-0 pt-0"
              background-color="grey lighten-4"
              style="width: 80px"
              hide-details
              hide-spin-buttons
              flat
              @change="check(key)"
            />
          </template>
        </v-slider>
      </div>
      <v-btn
        color="secondary"
        class="update-button"
        @click="update"
      >
        {{
          t('modal.weights.update')
        }}
      </v-btn>
    </div>
  </v-navigation-drawer>
</template>

<style scoped>
.drawer {
  margin: 5px;
}

.update-button {
  width: 100%;
  margin-top: 1em;
}
</style>
