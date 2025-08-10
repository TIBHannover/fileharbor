<template>
  <v-app>
    <v-layout>
      <HeaderToolbar @toggle-drawer="drawer = !drawer" />

      <slot :drawer="drawer" />

      <FooterToolbar />
    </v-layout>

    <LoaderTemplate />
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import HeaderToolbar from '@/components/toolbars/HeaderToolbar.vue'
import FooterToolbar from '@/components/toolbars/FooterToolbar.vue'
import LoaderTemplate from '@/components/LoaderTemplate.vue'

const drawer = ref(true)
</script>