<template>
  <div v-if="resultList" style="height: 100%">
    <!-- <Umap v-if="view === 'umap'" :data="entries" />
      <GridCluster v-if="view === 'cluster'" :entries="entries" /> -->
    <ImageListViewerGrid v-if="view === 'ranked'" :entries="resultList" />
  </div>

  <!-- <Loader :updating="$asyncComputed.entries" />
    <ModalNoResults :entries="entries" /> -->
</template>

<script setup>
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useSearchStore } from '@/stores/search'
import ImageListViewerGrid from '@/components/ImageListViewerGrid.vue'

const searchStore = useSearchStore()
const { resultList } = storeToRefs(searchStore)

const view = ref('ranked')
</script>

<style></style>
