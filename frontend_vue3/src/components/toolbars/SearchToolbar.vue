<template>
  <v-toolbar
    class="px-2 mt-3 mb-2"
    density="compact"
    color="white"
    height="60"
    flat
  >
    <v-toolbar-title class="text-body-3 ml-0">
      <i18n-t
        keypath="search.bar.count"
        :plural="searchResults"
        :values="{ count: '' }"
      >
        <template #count>
          <strong>{{ searchResults }}</strong>
        </template>
      </i18n-t>
    </v-toolbar-title>

    <v-spacer />

    <v-pagination
      v-model="page"
      density="compact"
      rounded="circle"
      :length="Math.ceil(searchResults / itemsPerPage)"
      :total-visible="5"
      :disabled="viewModeLocal === '2d'"
      @update:model-value="onPageClick"
    />

    <v-spacer />

    <template #append>
      <v-select
        v-model="orderByLocal"
        :items="orderOptions"
        item-title="value"
        item-value="key"
        :disabled="viewModeLocal === '2d'"
        class="group-by text-body-3"
        variant="outlined"
        density="compact"
        color="grey"
        max-width="300"
        hide-details
        @update:model-value="onApplyGroupBy"
      >
        <template #prepend>
          {{ $t('search.bar.order-by.title') }}
        </template>

        <template #append>
          <v-btn
            density="compact"
            :icon="sortOrderLocal === 'asc' ? 'mdi-sort-ascending' : 'mdi-sort-descending'"
            color="grey"
            @click="onSortOrder"
          />
        </template>
      </v-select>

      <v-menu open-on-hover>
        <template #activator="{ props: menuProps }">
          <v-btn
            class="ml-1"
            icon="mdi-cog"
            density="compact"
            color="grey"
            v-bind="menuProps"
          />
        </template>

        <v-list
          class="py-0"
          selectable
        >
          <v-list-item
            v-for="option in viewOptions"
            :key="option.key"
            @click="onViewMode(option.key)"
          >
            <template #prepend>
              <v-icon
                icon="mdi-check-circle"
                :color="viewModeLocal === option.key ? 'black' : 'transparent'"
                :style="{ opacity: 1 }"
              />
            </template>

            <v-list-item-title>
              {{ option.value }}
            </v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
  </v-toolbar>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  searchResults: {
    type: Number,
    default: 0
  },
  itemsPerPage: {
    type: Number,
    default: 24
  },
  orderBy: {
    type: String,
    default: 'relevance'
  },
  sortOrder: {
    type: String,
    default: 'desc'
  },
  viewMode: {
    type: String,
    default: '1d'
  }
})

const emit = defineEmits([
  'applyPageChange',
  'applyGroupBy'  
])

const { t } = useI18n({ useScope: 'global' })

const page = ref(1)
const orderByLocal = ref(props.orderBy)
const sortOrderLocal = ref(props.sortOrder)
const viewModeLocal = ref(props.viewMode)

function onPageClick(newPage) {
  emit('applyPageChange', newPage)
}

const orderOptions = computed(() => ([
  { key: 'relevance',      value: t('search.bar.order-by.relevance') },
  { key: 'creation-date',  value: t('search.bar.order-by.creation-date') },
  { key: 'object-title',   value: t('search.bar.order-by.object-title') }
]))

const viewOptions = computed(() => ([
  { key: '1d',             value: t('search.bar.view-mode.1d') },
  { key: '2d',             value: t('search.bar.view-mode.2d') }
]))

const onSortOrder = () => {
  sortOrderLocal.value = sortOrderLocal.value === 'asc' ? 'desc' : 'asc'
  onApplyGroupBy()
}

const onApplyGroupBy = () => {
  emit('applyGroupBy', {
    orderBy: orderByLocal.value,
    sortOrder: sortOrderLocal.value,
    viewMode: viewModeLocal.value
  })
}

const onViewMode = (value) => {
  viewModeLocal.value = value
  onApplyGroupBy()
}

watch(() => props.orderBy, (value) => orderByLocal.value = value)
watch(() => props.sortOrder, (value) => sortOrderLocal.value = value)
watch(() => props.viewMode, (value) => viewModeLocal.value = value)
</script>

<style scoped>
.v-toolbar-title {
  flex: none;
}
</style>

<style>
.group-by .v-field {
  text-transform: uppercase;
  font-weight: 500;
  letter-spacing: 1.25px;
  color: rgb(158 158 158);
  font-size: 14px;
  padding-right: 10px;
}

.group-by .v-field__outline__start,
.group-by .v-field__outline__notch,
.group-by .v-field__outline__end {
  color: rgb(158 158 158);
}

.group-by .v-field__input {
  min-height: 20px;
  padding: 8px 5px 7px 10px;
}
</style>