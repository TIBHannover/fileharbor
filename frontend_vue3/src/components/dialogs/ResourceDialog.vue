<template>
  <v-dialog
    :model-value="modelValue"
    fullscreen
    transition="dialog-top-transition"
    @update:model-value="val => $emit('update:modelValue', val)"
  >
    <v-card elevation="0">
      <v-container fluid>
        <v-row class="pa-0">
          <v-col
            class="pa-6 border-e-sm"
            cols="6"
          >
            <div class="text-h5 font-weight-bold">
              {{ titles[0] }}
            </div>

            <div class="text-grey mt-1">
              {{ formattedYears }}
            </div>

            <div class="mt-8">
              <div
                v-for="(names, field) in metadata"
                :key="`${field}:${names}`"
                class="py-2"
              >
                <div class="text-body-3">
                  {{ $t(`search.drawer.field.meta.${field}`) }}
                </div>

                <div class="mt-2">
                  <v-chip
                    v-for="name in names"
                    :key="name"
                    class="mr-1 mb-1"
                    @click="onFilter(`meta.${field}`, name)"
                  >
                    {{ name }}
                  </v-chip>
                </div>
              </div>
            </div>
          </v-col>

          <v-col
            class="d-flex flex-column pa-6"
            style="height: calc(100vh - 8px);"
            cols="6"
          >
            <v-row
              class="ma-0"
              style="flex: 0;"
              justify="end"
            >
              <v-btn
                icon="mdi-close"
                variant="flat"
                density="compact"
                @click="close"
              />
            </v-row>

            <v-row class="ma-0" />

            <v-row
              class="ma-0"
              style="flex: 0;"
              align="center"
              justify="center"
            >
              <v-img
                :src="item.path"
                :alt="titles[0]"
                class="bg-grey-lighten-2"
                loading="lazy"
                decoding="async"
                width="100%"
                max-height="500"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    justify="center"
                    align="center"
                  >
                    <v-progress-circular indeterminate />
                  </v-row>
                </template>
              </v-img>

              <v-btn
                class="mt-4"
                color="grey"
                variant="outlined"
                block
                @click="onApply"
              >
                {{ $t('resource.apply') }}
              </v-btn>
            </v-row>

            <v-row class="ma-0" />

            <v-row
              class="ma-0"
              style="flex: 0;"
            >
              <ImageCarousel :item="item" />
            </v-row>
          </v-col>
        </v-row>
      </v-container>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed } from 'vue'
import { useSearchStore } from '@/stores/search'
import useResource from '@/composables/useResource'
import ImageCarousel from '@/components/ImageCarousel.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  item: {
    type: Object,
    required: true
  }
})

const {
  isLoaded,
  isDisabled,
  onLoad,
  onError,
  titles,
  years,
  metadata
} = useResource(props.item)

const search = useSearchStore()

const emit = defineEmits(['update:modelValue'])
function close () {
  emit('update:modelValue', false)
}

const formattedYears = computed(() => {
  const [min, max] = years.value || []
  if (min == null && max == null) return ''
  if (min === max) return min
  const left = (min > -9999) ? `${min}–` : ''
  const right = (max < 9999) ? `${max}` : ''
  return `${left}${right}`.trim()
})

const onFilter = (field, name) => {
  const payload = [{ field, name: [name] }]
  search.setFilters(payload)
  search.post()
  close()
}

const onApply = () => {
  const payload = {
    modality: 'images',
    query: { value: props.item.id }
  }
  search.removeFilters()
  search.post(payload)
  close()
}
</script>

<style scoped>
.v-dialog {
  max-width: 1200px;
}
</style>