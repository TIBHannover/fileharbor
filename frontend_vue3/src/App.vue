<template>
  <component
    :is="layout"
    v-slot="{ drawer }"
  >
    <RouterView v-slot="{ Component }">
      <component
        :is="Component"
        :drawer="drawer"
      />
    </RouterView>
  </component>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'

const route = useRoute()

const layout = computed(() => route.meta.layout || DefaultLayout)
</script>