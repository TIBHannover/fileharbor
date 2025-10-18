<template>
  <v-navigation-drawer
    :model-value="modelValue"
    width="400"
  >
    <v-row no-gutters>
      <v-col class="pa-6">
        <div class="text-caption text-uppercase text-medium-emphasis mb-2">
          {{ $t("search.bar.title") }}
        </div>

        <ParamsField />
      </v-col>
    </v-row>

    <template v-if="filteredData.length">
      <v-divider />

      <div class="text-caption text-uppercase text-medium-emphasis mx-6 mt-6">
        {{ $t("search.drawer.title") }}
      </div>

      <v-expansion-panels
        v-model="panel"
        class="overflow-y-auto"
        variant="accordion"
        :max="3"
        multiple
        static
        flat
      >
        <v-expansion-panel
          v-for="record in filteredData"
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
              v-if="record.field === 'meta/time/start'"
              :data="record.entries"
              @update-years="onUpdateYears"
            >
              <v-row class="mt-2">
                <v-col>
                  <v-number-input
                    :model-value="selectedEntries['meta/time/start']"
                    :placeholder="String(Math.min(...years))"
                    control-variant="stacked"
                    variant="outlined"
                    density="compact"
                    hide-details
                    clearable
                    rounded
                    inset
                    @update:model-value="val => (selectedEntries['meta/time/start'] = val)"
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
                    :model-value="selectedEntries['meta/time/end']"
                    :placeholder="String(Math.max(...years))"
                    control-variant="stacked"
                    variant="outlined"
                    density="compact"
                    hide-details
                    clearable
                    rounded
                    inset
                    @update:model-value="val => (selectedEntries['meta/time/end'] = val)"
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
                v-if="isGeographicEntries(record.entries)"
                :data="record.entries"
                class="mb-4"
              />

              <BarChartPanel
                v-else-if="!isNumericEntries(record.entries)"
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
    </template>
  </v-navigation-drawer>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import MapPanel from '@/components/panels/MapPanel.vue'
import BarChartPanel from '@/components/panels/BarChartPanel.vue'
import HistogramPanel from '@/components/panels/HistogramPanel.vue'
import ParamsField from '@/components/ParamsField.vue'

const props = defineProps({
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

const filteredData = computed(() =>
  (props.data ?? []).filter(r => r.field.startsWith('meta/'))
)

const isGeographicEntries = (entries) => {
  if (!Array.isArray(entries) || entries.length === 0) return false
  const withCoords = entries.filter(e => e.lat && e.lon).length
  return withCoords / entries.length >= 0.75
}

const isNumericEntries = (entries) => {
  if (!Array.isArray(entries) || entries.length === 0) return false
  return entries.every(e => typeof e.name === 'number')
}

const panel = ref([0])
const years = ref([])
const selectedEntries = reactive({})

const selectedFields = computed(() => new Set(Object.keys(selectedEntries)))
const isSelectedField = (field) => selectedFields.value.has(field)

const selectionCounts = computed(() => {
  const yearKeys = ["meta/time/start", "meta/time/end"]
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

watch(panel, (value) => {
  if (value.length > 2) {
    panel.value = value.slice(-2)
  }
})
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