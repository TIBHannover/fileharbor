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
      @update:model-value="onPageClick"
    />

    <v-spacer />

    <template #append>
      <v-select
        v-model="orderBy"
        :items="orderOptions"
        item-title="value"
        item-value="key"
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
            :icon="sortOrder == 'asc' ? 'mdi-sort-ascending' : 'mdi-sort-descending'"
            color="grey"
            @click="onSortOrder"
          />
        </template>
      </v-select>

      <v-menu open-on-hover>
        <template #activator="{ props }">
          <v-btn
            class="ml-1"
            icon="mdi-cog"
            density="compact"
            color="grey"
            v-bind="props"
          />
        </template>

        <v-list>
          <v-list-item>
            TODO
          </v-list-item>
        </v-list>
      </v-menu>
    </template>
  </v-toolbar>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps({
  searchResults: {
    type: Number,
    default: 0
  },
  itemsPerPage: {
    type: Number,
    default: 24
  }
})

const { t } = useI18n({ useScope: 'global' })
const emit = defineEmits([
  'applyPageChange',
  'applyGroupBy'  
])

const page = ref(1)

function onPageClick(newPage) {
  emit('applyPageChange', newPage)
}

const orderBy = ref('relevance')
const sortOrder = ref('desc')

const orderOptions = computed(() => ([
  { key: 'relevance',      value: t('search.bar.order-by.relevance') },
  { key: 'creation-date',  value: t('search.bar.order-by.creation-date') },
  { key: 'object-title',   value: t('search.bar.order-by.object-title') }
]))

const onSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  onApplyGroupBy()
}

const onApplyGroupBy = () => {
  const payload = {
    orderBy: orderBy.value,
    sortOrder: sortOrder.value
  }
  emit('applyGroupBy', payload)
}
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