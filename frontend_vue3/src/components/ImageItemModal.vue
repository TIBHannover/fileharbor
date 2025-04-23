<template>
  <div class="flex-view">
    <ImageItem v-for="(entry, index) in entries" :entry="entry" />

    <div class="grid-item-fill"></div>

    <!-- <v-pagination
        v-if="nPages > 1"
        v-model="page"
        :length="nPages"
        :total-visible="6"
        class="mt-4"
        color="accent"
        circle
      /> -->
  </div>
</template>

<script setup>
import ImageItem from '@/components/ImageItem.vue'

const props = defineProps({
  entries: Array,
})
</script>

<style>
.flex-view {
  flex-grow: 1;
  display: flex;
  flex-wrap: wrap;
  overflow: hidden;
  transition: flex-basis 0.2s ease;
}

.flex-view:after {
  content: '';
  flex: auto;
}

.grid-item-fill {
  flex-grow: 150;
}

nav[role='navigation'] {
  text-align: center;
  width: 100%;
}

nav[role='navigation'] button {
  box-shadow: none;
}

nav[role='navigation'] button:focus {
  outline: none;
}

.theme--light.v-pagination .v-pagination__item--active.accent {
  color: #fff !important;
}
</style>
