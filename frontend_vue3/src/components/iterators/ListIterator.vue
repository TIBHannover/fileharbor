<template>
  <v-data-iterator
    :items="entries"
    :items-per-page="itemsPerPage"
    hide-default-footer
  >
    <template #default="{ items }">
      <v-row v-if="itemsPerRow <= 12">
        <v-col
          v-for="item in items"
          :key="item.raw.id"
          :cols="(12 / itemsPerRow)"
          class="pt-0 pb-2 px-1"
        >
          <SearchCard
            :item="item.raw"
            :is-flex="false"
          />
        </v-col>
      </v-row>

      <v-row v-else>
        <SearchCard
          v-for="item in items"
          :key="item.raw.id"
          :item="item.raw"
          :is-flex="true"
        />

        <div class="grid-item-fill" />
      </v-row>
    </template>

    <template #no-data>
      <!-- TODO: empty state -->
    </template>
  </v-data-iterator>
</template>

<script setup>
import SearchCard from '@/components/cards/SearchCard.vue'

defineProps({
  entries: {
    type: Array,
    required: true
  },
  itemsPerPage: {
    type: Number,
    default: 96
  },
  itemsPerRow: {
    type: Number,
    default: 4
  }
})
</script>

<style scoped>
.grid-item-fill {
  flex-grow: 150;
}
</style>