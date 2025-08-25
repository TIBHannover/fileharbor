<template>
  <v-navigation-drawer
    :model-value="modelValue"
    class="overflow-y-auto pt-2"
    width="400"
    app
  >
    <v-expansion-panels
      v-model="panel"
      variant="accordion"
      multiple
      static
      flat
    >
      <v-expansion-panel
        v-for="record in data"
        :key="record.field"
      >
        <v-expansion-panel-title>
          {{ $t(`search.drawer.field.${record.field}`) }}

          <span
            v-if="selectionCounts[record.field] > 0"
            class="ml-2"
          >
            <i18n-t
              keypath="search.drawer.count"
              :plural="selectionCounts[record.field]"
              :values="{ count: '' }"
            >
              <template #count>
                <strong>{{ selectionCounts[record.field] }}</strong>
              </template>
            </i18n-t>
          </span>

          <template #actions="{ expanded }">
            <v-btn
              v-if="selectionCounts[record.field] > 0"
              class="mr-1"
              variant="text"
              density="compact"
              color="grey"
              icon="mdi-refresh"
              @click.stop="clearField(record.field)"
            />

            <v-btn
              variant="text"
              density="compact"
              color="grey"
              :icon="expanded ? 'mdi-minus-circle-outline' : 'mdi-plus-circle-outline'"
            />
          </template>
        </v-expansion-panel-title>

        <v-expansion-panel-text>
          <HistogramPanel
            v-if="record.field === 'meta.year_min'"
            :data="record.entries"
            @update-years="onUpdateYears"
          >
            <v-row class="mt-2">
              <v-col>
                <v-number-input
                  :model-value="selectedEntries['meta.year_min']"
                  :placeholder="String(Math.min(...years))"
                  :min="Math.min(...years)"
                  :max="Math.max(...years)"
                  control-variant="stacked"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                  rounded
                  inset
                  @update:model-value="val => (selectedEntries['meta.year_min'] = val)"
                >
                  <template #clear>
                    <v-icon size="14">
                      mdi-close
                    </v-icon>
                  </template>
                </v-number-input>
              </v-col>

              <v-col
                cols="auto"
                class="d-flex align-center px-0"
              >
                –
              </v-col>

              <v-col>
                <v-number-input
                  :model-value="selectedEntries['meta.year_max']"
                  :placeholder="String(Math.max(...years))"
                  :min="Math.min(...years)"
                  :max="Math.max(...years)"
                  control-variant="stacked"
                  variant="outlined"
                  density="compact"
                  hide-details
                  clearable
                  rounded
                  inset
                  @update:model-value="val => (selectedEntries['meta.year_max'] = val)"
                >
                  <template #clear>
                    <v-icon size="14">
                      mdi-close
                    </v-icon>
                  </template>
                </v-number-input>
              </v-col>
            </v-row>
          </HistogramPanel>

          <template v-else>
            <MapPanel
              v-if="record.field === 'meta.location'"
              :data="record.entries"
              class="mb-4"
            />

            <BarChartPanel
              v-if="record.field === 'meta.depicts'"
              :data="record.entries"
            />

            <v-virtual-scroll
              :items="record.entries"
              item-key="name"
              max-height="250"
              item-height="28"
            >
              <template #default="{ item }">
                <v-list-item class="pa-0">
                  <v-list-item-title>
                    <v-checkbox
                      :model-value="selectedEntries[record.field] ?? []"
                      :value="item.name"
                      density="compact"
                      hide-details
                      @update:model-value="val => (selectedEntries[record.field] = val)"
                    >
                      <template #label>
                        <div class="text-body-2 ml-1">
                          {{ item.name }}
                          (<b>{{ item.count }}</b>)
                        </div>
                      </template>
                    </v-checkbox>
                  </v-list-item-title>
                </v-list-item>
              </template>
            </v-virtual-scroll>
          </template>

          <div
            v-show="isSelectedField(record.field)"
            class="actions mt-4"
          >
            <v-btn
              color="grey"
              variant="outlined"
              block
              @click="onApply"
            >
              {{ $t('search.drawer.apply') }}
            </v-btn>
          </div>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import MapPanel from '@/components/panels/MapPanel.vue'
import BarChartPanel from '@/components/panels/BarChartPanel.vue'
import HistogramPanel from '@/components/panels/HistogramPanel.vue'

defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  data: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['apply'])

const panel = ref([0])
const years = ref([])
const selectedEntries = reactive({})

const selectedFields = computed(() => new Set(Object.keys(selectedEntries)))
const isSelectedField = (field) => selectedFields.value.has(field)

const selectionCounts = computed(() => {
  const yearKeys = ["meta.year_min", "meta.year_max"]
  const hasRange = yearKeys.every((k) =>
    Object.prototype.hasOwnProperty.call(selectedEntries, k)
  )

  return Object.fromEntries(
    Object.entries(selectedEntries)
      .map(([k, v]) => {
        if (Array.isArray(v)) return [k, v.length]
        if (typeof v === "string") return [k, 1]

        if (typeof v === "number") {
          return [k, hasRange && yearKeys.includes(k) ? 2 : 1]
        }

        return [k, 0]
      })
  )
})

const onUpdateYears = (values) => {
  years.value = values
}

const onApply = () => {
  const payload = Object.entries(selectedEntries)
    .filter(([, v]) =>
      Array.isArray(v) ? v.length > 0
      : typeof v === "string" ? v.trim() !== ""
      : typeof v === "number" ? Number.isFinite(v)
      : typeof v === "boolean" ? true
      : false
    )
    .map(([k, v]) => ({
      field: k,
      name: Array.isArray(v) ? v.slice() : v
    }))

  emit('apply', payload)
}

const clearField = (field) => {
  selectedEntries[field] = []
  onApply()
}
</script>

<style scoped>
.v-input--density-compact {
  --v-input-control-height: 28px;
}

.v-list-item--density-default {
  min-height: 28px;
}
</style>

<style>
.v-input--density-compact .v-input__control,
.v-input--density-compact .v-selection-control,
.v-input--density-compact .v-selection-control .v-label > div {
  width: 100%;
}

.v-input--density-compact .v-selection-control .v-label > div {
  overflow: clip;
  white-space: nowrap;
  text-overflow: ellipsis;
}
</style>