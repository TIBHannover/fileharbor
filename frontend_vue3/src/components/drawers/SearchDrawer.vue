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
      flat
    >
      <DatePanel />
      <LocationPanel />

      <v-expansion-panel
        v-for="record in data"
        :key="record.field"
        static
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
import DatePanel from '@/components/panels/DatePanel.vue'
import LocationPanel from '@/components/panels/LocationPanel.vue'

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
const selectedEntries = reactive({})

const selectedFields = computed(() => new Set(Object.keys(selectedEntries)))
const isSelectedField = (field) => selectedFields.value.has(field)

const selectionCounts = computed(() => {
  const out = {}
  for (const k of Object.keys(selectedEntries)) {
    out[k] = (selectedEntries[k] || []).length
  }
  return out
})

const countFieldSelections = (field) =>
  selectedEntries[field].length

const onApply = () => {
  // clone arrays to avoid exposing reactive refs
  const payload = {}
  for (const [k, v] of Object.entries(selectedEntries)) {
    if (Array.isArray(v) && v.length) payload[k] = [...v]
  }
  emit('apply', payload)
}

const clearField = field => {
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