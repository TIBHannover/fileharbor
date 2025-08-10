<template>
  <v-toolbar
    class="px-2 mt-3"
    density="compact"
    color="white"
    height="60"
    flat
  >
    <v-toolbar-title class="text-body-3 ml-0">
      <i18n-t
        keypath="search.bar.count"
        :plural="count"
        :values="{ count: '' }"
      >
        <template #count>
          <strong>{{ count }}</strong>
        </template>
      </i18n-t>
    </v-toolbar-title>

    <template #append>
      <v-select
        v-model="orderBy"
        :items="[
          $t('search.bar.order-by.relevance'),
          $t('search.bar.order-by.creation-date'),
          $t('search.bar.order-by.object-title')
        ]"
        :item-value="$t('search.bar.order-by.relevance')"
        class="group-by text-body-3"
        variant="outlined"
        density="compact"
        color="grey"
        max-width="300"
        hide-details
        @update:model-value="onApply"
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
    </template>
  </v-toolbar>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'

defineProps({
  count: {
    type: Number,
    default: 0
  }
})

const { t } = useI18n()

const emit = defineEmits(['apply'])

const orderBy = ref(t('search.bar.order-by.relevance'))
const sortOrder = ref('asc')

const onSortOrder = () => {
  sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  onApply()
}

const onApply = () => {
  const payload = {
    orderBy: orderBy.value,
    sortOrder: sortOrder.value
  }
  emit('apply', payload)
}
</script>

<style scoped>
.v-toolbar-title {
  flex: none;
}

.text-body-3 {
  font-size: 15px;
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