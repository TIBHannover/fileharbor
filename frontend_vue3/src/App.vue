<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import logo from '@/assets/logo.png'
import SearchBar from '@/components/SearchBar.vue'
import ImageListViewer from '@/components/ImageListViewer.vue'

import { useSearchStore } from '@/stores/search'
import { useHelper } from '@/composables/helper'

const searchStore = useSearchStore()
const { isLoading } = storeToRefs(searchStore)

let fetchSearchResultsTimer = null

watch(isLoading, (n, o) => {
  if (n) {
    fetchSearchResultsTimer = setInterval(() => {
      searchStore.fetchSearchResults()
    }, 1000)
  }
  if (!n) {
    clearInterval(fetchSearchResultsTimer)
  }
  console.log(n)
})

const theme = ref('light')

function onClick() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}
</script>

<template>
  <v-app :theme="theme">
    <v-app-bar class="px-3">
      <div class="logo ml-3 mr-5" @click="reset">
        <img title="iART" :src="logo" />
      </div>
      <SearchBar></SearchBar>

      <v-btn
        :icon="theme === 'light' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        @click="onClick"
      ></v-btn>
    </v-app-bar>
    <!-- <v-navigation-drawer expand-on-hover>
      <v-expansion-panels>
        <v-expansion-panel
          v-for="i in 3"
          :key="i"
          text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
          title="Item"
        ></v-expansion-panel>
      </v-expansion-panels>
    </v-navigation-drawer> -->
    <v-main>
      <ImageListViewer />
    </v-main>
  </v-app>

  <RouterView />
</template>

<style scoped>
.logo {
  align-items: center;
  cursor: pointer;
  display: flex;
}

.logo > img {
  max-height: 28px;
}
</style>
