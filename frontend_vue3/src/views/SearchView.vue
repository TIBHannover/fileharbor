<template>
  <v-app :theme="theme">
    <v-app-bar class="px-3">
      <div
        class="logo ml-3 mr-5"
        @click="reset"
      >
        <img
          title="iART"
          src="/logo.png"
        >
      </div>
      <SearchBar />

      <v-btn
        :icon="theme === 'light' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
        @click="onClick"
      />
    </v-app-bar>
    <v-navigation-drawer
      permanent
      rail
    >
      <v-list
        v-model:selected="nav"
        density="compact"
        nav
      >
        <v-list-item
          prepend-icon="mdi-tune-variant"
          value="tune"
        />
        <v-list-item
          prepend-icon="mdi-filter"
          value="filter"
        />
        <v-list-item
          prepend-icon="mdi-view-dashboard-edit"
          value="view"
        />
        <v-list-item
          prepend-icon="mdi-forum"
          value="chat"
        />
        <v-list-item
          prepend-icon="mdi-graph"
          value="graph"
        />
        <v-list-item
          prepend-icon="mdi-export"
          value="export"
        />
      </v-list>
    </v-navigation-drawer>

    <WeightsDrawer v-model="tuneDrawer" />
    <v-navigation-drawer v-model="filterDrawer" />
    <v-navigation-drawer v-model="viewDrawer" />
    <v-navigation-drawer v-model="chatDrawer" />
    <v-navigation-drawer v-model="graphDrawer" />
    <v-navigation-drawer v-model="exportDrawer" />

    <v-main>
      <ImageListViewer />
    </v-main>
  </v-app>

  <RouterView />
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, watch, computed } from 'vue'
import { storeToRefs } from 'pinia'
import SearchBar from '@/components/SearchBar.vue'
import ImageListViewer from '@/components/ImageListViewer.vue'
import WeightsDrawer from '@/components/drawers/WeightsDrawer.vue'

import { useSearchStore } from '@/stores/search'

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
})

const theme = ref('light')

function onClick() {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
}

const nav = ref(null)

watch(nav, (n, o) => {
  console.log(n[0])
})

const tuneDrawer = computed({
  get() {
    if (Array.isArray(nav.value)) {
      return nav.value[0] === 'tune'
    }
    return false
  },
  set(n) {
    if (n === false) {
      nav.value = []
    }
  },
})

const viewDrawer = computed({
  get() {
    if (Array.isArray(nav.value)) {
      return nav.value[0] === 'view'
    }
    return false
  },
  set(n) {
    if (n === false) {
      nav.value = []
    }
  },
})

const filterDrawer = computed({
  get() {
    if (Array.isArray(nav.value)) {
      return nav.value[0] === 'filter'
    }
    return false
  },
  set(n) {
    if (n === false) {
      nav.value = []
    }
  },
})

const chatDrawer = computed({
  get() {
    if (Array.isArray(nav.value)) {
      return nav.value[0] === 'chat'
    }
    return false
  },
  set(n) {
    if (n === false) {
      nav.value = []
    }
  },
})

const graphDrawer = computed({
  get() {
    if (Array.isArray(nav.value)) {
      return nav.value[0] === 'graph'
    }
    return false
  },
  set(n) {
    if (n === false) {
      nav.value = []
    }
  },
})

const exportDrawer = computed({
  get() {
    if (Array.isArray(nav.value)) {
      return nav.value[0] === 'export'
    }
    return false
  },
  set(n) {
    if (n === false) {
      nav.value = []
    }
  },
})
</script>

<style scoped>
.second-drawer {
  margin: 5px;
}

.logo {
  align-items: center;
  cursor: pointer;
  display: flex;
}

.logo > img {
  max-height: 28px;
}
</style>
