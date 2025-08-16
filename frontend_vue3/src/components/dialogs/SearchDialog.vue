<template>
  <v-dialog
    v-model="dialog"
    class="search"
    fullscreen
    transition="dialog-top-transition"
  >
    <template #activator="{ props: activatorProps }">
      <template v-if="$slots.activator">
        <span
          class="inline-flex"
          v-bind="activatorProps"
        >
          <slot name="activator" />
        </span>
      </template>
      <template v-else>
        <v-btn
          icon="mdi-magnify"
          v-bind="activatorProps"
        />
      </template>
    </template>

    <v-toolbar
      class="px-3"
      color="accent"
      flat
    >
      <template #append>
        <v-btn
          icon="mdi-close"
          density="compact"
          @click="dialog = false"
        />
      </template>
    </v-toolbar>

    <v-card elevation="0">
      <v-container
        class="py-8"
        style="max-width: 750px;"
      >
        <!-- Modality -->
        <div class="pb-4">
          <div class="text-body-3">
            {{ $t("search.dialog.modality.title") }}
          </div>

          <div class="d-flex mt-3">
            <v-slide-group
              v-model="modalityLocal"
              class="me-auto"
            >
              <v-slide-group-item
                v-for="option in modalityOptions"
                :key="option.key"
                v-slot="{ isSelected, toggle }"
                :value="option.key"
              >
                <v-chip
                  class="mr-2"
                  :disabled="option.disabled"
                  color="grey"
                  @click="toggle"
                >
                  <template #prepend>
                    <v-icon
                      v-if="isSelected"
                      class="mr-2"
                      color="grey-darken-4"
                      icon="mdi-check-circle"
                    />

                    <v-icon
                      v-if="option.disabled"
                      class="mr-2"
                      color="grey-darken-4"
                      icon="mdi-progress-wrench"
                    />
                  </template>

                  <span class="text-grey-darken-4">
                    {{ option.value }}
                  </span>
                </v-chip>
              </v-slide-group-item>
            </v-slide-group>

            <div class="d-flex align-center ml-2">
              <v-btn
                :disabled="true"
                icon="mdi-information-outline"
                density="compact"
                variant="text"
                size="small"
              />
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="py-4">
          <div class="text-body-3">
            {{ $t("search.dialog.input.title") }}
          </div>

          <v-text-field
            v-if="modalityLocal === 'text'"
            v-model="inputText"
            class="mt-3"
            :placeholder="t('search.dialog.input.text')"
            prepend-inner-icon="mdi-magnify"
            variant="outlined"
            hide-details
            clearable
            rounded
            flat
          />

          <v-file-input
            v-if="modalityLocal === 'images'"
            v-model="inputImages"
            class="mt-3"
            :placeholder="t('search.dialog.input.images')"
            prepend-inner-icon="mdi-magnify"
            prepend-icon=""
            accept="image/*"
            variant="outlined"
            hide-details
            clearable
            multiple
            rounded
            flat
          >
            <template #prepend-inner>
              <div
                v-if="!inputImages || inputImages.length === 0"
                class="text-grey ml-1"
                style="min-width: 150px;"
              >
                {{ $t("search.dialog.input.images") }}
              </div>
            </template>
          </v-file-input>
        </div>

        <!-- Similarity (images only) -->
        <div
          v-if="modalityLocal === 'images'"
          class="py-4"
        >
          <div class="text-body-3">
            {{ $t("search.dialog.similarity.title") }}
          </div>

          <div class="d-flex mt-3">
            <v-slide-group
              v-model="similarityLocal"
              class="me-auto"
              multiple
            >
              <v-slide-group-item
                v-for="option in similarityOptions"
                :key="option.key"
                v-slot="{ isSelected, toggle }"
                :value="option.key"
              >
                <v-chip
                  :disabled="option.disabled"
                  class="mr-2"
                  color="grey"
                  @click="toggle"
                >
                  <template #prepend>
                    <v-icon
                      v-if="isSelected"
                      class="mr-2"
                      color="grey-darken-4"
                      icon="mdi-check-circle"
                    />

                    <v-icon
                      v-if="option.disabled"
                      class="mr-2"
                      color="grey-darken-4"
                      icon="mdi-progress-wrench"
                    />
                  </template>

                  <span class="text-grey-darken-4">
                    {{ option.value }}
                  </span>
                </v-chip>
              </v-slide-group-item>
            </v-slide-group>

            <div class="d-flex align-center ml-2">
              <v-btn
                icon="mdi-cog"
                density="compact"
                variant="text"
                size="small"
                @click="similaritySettings = !similaritySettings"
              />
            </div>
          </div>

          <div
            v-if="similaritySettings"
            class="mt-3"
          >
            <v-slider
              v-for="option in similarityOptions"
              :key="option.key"
              v-model="similarityValues[option.key]"
              :label="option.value"
              class="mx-0 mt-1"
              :disabled="!isSimilaritySelected(option.key)"
              min="0"
              :max="maxValue"
              step="1"
              density="compact"
              thumb-size="16"
              elevation="0"
              hide-details
              @end="onSimilarityInput(option.key, $event)"
            >
              <template #append>
                <v-text-field
                  class="number"
                  style="width: 85px;"
                  :disabled="!isSimilaritySelected(option.key)"
                  type="number"
                  min="0"
                  :max="maxValue"
                  step="1"
                  variant="outlined"
                  density="compact"
                  hide-details
                  rounded
                  :model-value="similarityValues[option.key]"
                  @end="onSimilarityInput(option.key, $event)"
                />
              </template>
            </v-slider>
          </div>
        </div>

        <!-- Dataset -->
        <div class="py-4">
          <div class="text-body-3">
            {{ $t("search.dialog.dataset.title") }}
          </div>

          <v-slide-group
            v-model="datasetLocal"
            class="mt-3"
            show-arrows="always"
            multiple
          >
            <v-slide-group-item
              v-for="option in datasetOptions"
              :key="option.key"
              v-slot="{ isSelected, toggle }"
              :value="option.key"
            >
              <v-btn
                class="mr-2"
                color="grey"
                variant="outlined"
                min-width="150"
                height="75"
                @click="toggle"
              >
                <template #prepend>
                  <v-icon
                    v-if="isSelected"
                    color="grey-darken-4"
                    icon="mdi-check-circle"
                  />
                </template>

                <div class="text-none">
                  <div class="text-grey-darken-4">
                    {{ option.value }}
                  </div>

                  <div class="text-caption text-grey-darken-1">
                    X Objects
                  </div>
                </div>
              </v-btn>
            </v-slide-group-item>
          </v-slide-group>
        </div>

        <v-btn
          class="mt-4"
          color="grey"
          variant="outlined"
          block
          @click="onApply"
        >
          {{ $t('search.dialog.apply') }}
        </v-btn>
      </v-container>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useSearchStore } from '@/stores/search'

const props = defineProps({
  modality: {
    type: String,
    default: 'text'
  },
  similarity: {
    type: Array,
    default: () => ['content']
  },
  dataset: {
    type: Array,
    default: () => ['wikidata']
  }
})

const emit = defineEmits([
  'update:modality',
  'update:similarity',
  'update:dataset'
])

const search = useSearchStore()
const { t } = useI18n({ useScope: 'global' })

const dialog = ref(false)
const maxValue = 100

const inputText = ref('')
const inputImages = ref([])
const inputIconclass = ref('')

const modalityLocal = ref(props.modality)
const similarityLocal = ref([...props.similarity])
const similaritySettings = ref(false)
const datasetLocal = ref([...props.dataset])

const modalityOptions = computed(() => ([
  { key: 'text',        value: t('search.dialog.modality.text') },
  { key: 'images',      value: t('search.dialog.modality.images') },
  { key: 'iconclass',   value: t('search.dialog.modality.iconclass'),     disabled: true }
]))

const similarityOptions = computed(() => ([
  { key: 'color',       value: t('search.dialog.similarity.color') },
  { key: 'composition', value: t('search.dialog.similarity.composition') },
  { key: 'content',     value: t('search.dialog.similarity.content') },
  { key: 'form',        value: t('search.dialog.similarity.form'),        disabled: true },
  { key: 'posture',     value: t('search.dialog.similarity.posture') },
  { key: 'style',       value: t('search.dialog.similarity.style') }
]))

const datasetOptions = computed(() => ([
  { key: 'wikidata',    value: t('search.dialog.dataset.wikidata') },
  { key: 'kenom',       value: t('search.dialog.dataset.kenom') },
  { key: 'artigo',      value: t('search.dialog.dataset.artigo') },
  { key: 'other-1',     value: t('search.dialog.dataset.other') },
  { key: 'other-2',     value: t('search.dialog.dataset.other') },
  { key: 'other-3',     value: t('search.dialog.dataset.other') }
]))

const similarityValues = reactive(
  similarityOptions.value.reduce((acc, o) => {
    acc[o.key] = 0
    return acc
  }, {})
)

const isSimilaritySelected = (key) => similarityLocal.value.includes(key)

const onSimilarityInput = (editedKey, newValue) => {
  const others = similarityLocal.value.filter(k => k !== editedKey)
  const otherWeights = others.map(k => ({ k, w: similarityValues[k] }))

  if (others.length) {
    const remaining = Math.max(0, maxValue - newValue)
    const sumW = otherWeights.reduce((s, x) => s + x.w, 0)

    otherWeights.forEach(({ k, w }) => {
      similarityValues[k] = Math.floor( w / sumW * remaining)
    })
  } else {
    newValue = maxValue
  }

  similarityValues[editedKey] = newValue
}

watch(
  similarityLocal,
  () => {
    for (const o of similarityOptions.value) {
      similarityValues[o.key] = 0
    }

    const selected = similarityLocal.value
    const n = selected.length
    if (n === 0) return

    selected.forEach((key) => {
      similarityValues[key] = Math.round(maxValue / n)
    })
  },
  { immediate: true }
)

const onApply = () => {
  emit('update:modality', modalityLocal.value)
  emit('update:similarity', similarityLocal.value)
  emit('update:dataset', datasetLocal.value)

  const payload = {
    modality: modalityLocal.value,
    dataset: [...datasetLocal.value]
  }

  if (payload.modality === 'text') {
    payload.query = inputText.value?.trim() || ''
  } else if (payload.modality === 'images') {
    payload.query = [...inputImages.value] || []
    let values = Object.entries(similarityValues)
    values = values.filter(([, v]) => v > 0)
    payload.similarity = Object.fromEntries(values)
  } else if (payload.modality === 'iconclass') {
    payload.query = inputIconclass.value?.trim() || ''
  }

  console.log(payload)
  search.post(payload)
  dialog.value = false
}
</script>

<style>
.v-dialog.search > .v-overlay__content {
  height: auto;
}

.v-dialog.search .v-slider .v-label {
  min-width: 90px;
}

.v-dialog.search .v-slider .v-label,
.v-dialog.search .v-input.number input {
  font-size: 0.875rem;
}
</style>