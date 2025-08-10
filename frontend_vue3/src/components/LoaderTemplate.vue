<template>
  <div
    v-if="status.loading"
    class="loading"
  >
    <v-progress-circular
      color="error"
      indeterminate
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useUtilsStore } from '@/stores/utils'

const utils = useUtilsStore()
const { status } = storeToRefs(utils)
</script>

<style scoped>
.loading {
  background-color: rgba(0 0 0 / 30%);
  text-align: center;
  position: fixed;
  z-index: 999;
  inset: 0;
}

.loading > div {
  height: 100% !important;
}
</style>