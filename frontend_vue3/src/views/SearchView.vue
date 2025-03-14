<script setup>
import { RouterLink, RouterView } from 'vue-router'
import { ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import logo from '@/assets/logo.png'
import SearchBar from '@/components/SearchBar.vue'

import { useSearchStore } from '@/stores/search'
import { useHelper } from '@/composables/helper'

const searchStore = useSearchStore()
const { isLoading } = storeToRefs(searchStore)

console.log(isLoading.value)
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
  <v-responsive class="border rounded" max-height="300">
    <v-app :theme="theme">
      <v-app-bar class="px-3">
        <div class="logo ml-3 mr-5" @click="reset">
          <img :title="appName" :src="logo" />
        </div>
        <SearchBar></SearchBar>

        <v-btn
          :icon="theme === 'light' ? 'mdi-weather-sunny' : 'mdi-weather-night'"
          @click="onClick"
        ></v-btn>
      </v-app-bar>
      <v-navigation-drawer expand-on-hover>
        <v-expansion-panels>
          <v-expansion-panel
            v-for="i in 3"
            :key="i"
            text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
            title="Item"
          ></v-expansion-panel>
        </v-expansion-panels>
      </v-navigation-drawer>

      <v-main>
        <v-container>
          <h1>Main Content</h1>
        </v-container>
      </v-main>
    </v-app>
  </v-responsive>

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

.v-chip .v-avatar {
  padding-top: 3px;
}

.v-input .v-btn {
  letter-spacing: 1;
}

.v-application--is-ltr .v-text-field.v-text-field .v-input__prepend-inner {
  padding-right: 12px;
}

.v-select.v-select--is-menu-active .v-input__icon--append .v-icon {
  transform: rotate(0deg);
}

#search-general {
  display: flex;
  flex: 1 1 auto;
  max-width: 100%;
}

header #search-general {
  max-width: calc(100% - 327px);
}

.v-autocomplete:not(.v-input--is-focused).v-select--chips input {
  max-height: 25px !important;
}

header .v-autocomplete .v-text-field.v-text-field--solo .v-input__control input {
  max-width: fit-content;
  min-width: 0;
}

.sbar.v-autocomplete .v-select__selections {
  -ms-overflow-style: none;
  scrollbar-width: none;
  flex-wrap: nowrap;
  overflow-x: auto;
  overflow-y: hidden;
}

.sbar.v-autocomplete .v-select__selections::-webkit-scrollbar {
  height: 0;
  width: 0;
}

.sbar.v-autocomplete .v-select__selections > .v-chip {
  overflow: initial;
}

.theme--light.v-icon,
.v-dialog .v-expansion-panel-content__wrap .capitalize {
  color: rgba(69, 123, 157, 0.54);
}

.v-input__icon--append .theme--light.v-icon:not(.mdi-menu-down),
.v-input__prepend-inner .theme--light.v-icon {
  color: rgba(0, 0, 0, 0.54);
}

.v-main
  .theme--light.v-text-field--outlined:not(.v-input--is-focused):not(.v-input--has-state)
  > .v-input__control
  > .v-input__slot
  fieldset {
  border: 3px solid;
  color: #f5f5f5;
}

.v-main .v-text-field--outlined.v-input--has-state fieldset,
.v-main .v-text-field--outlined.v-input--is-focused fieldset {
  border: 3px solid;
}

header
  .theme--light.v-text-field--outlined:not(.v-input--is-focused):not(.v-input--has-state)
  > .v-input__control
  > .v-input__slot
  fieldset {
  border: 0px solid;
}

header .v-text-field--outlined.v-input--has-state fieldset,
header .v-text-field--outlined.v-input--is-focused fieldset {
  border: 0px solid;
}

header .v-text-field--filled > .v-input__control > .v-input__slot,
header .v-text-field--full-width > .v-input__control > .v-input__slot,
header .v-text-field--outlined > .v-input__control > .v-input__slot {
  min-height: 48px;
}

.v-chip__content .v-btn__content {
  justify-content: center;
}

.v-input.lang {
  font-family: 'Roboto Mono', monospace;
  text-transform: uppercase;
  width: min-content;
}

.v-input.lang > .v-input__control > .v-input__slot {
  padding: 0 6px !important;
}

.v-input.lang > .v-input__control .v-select__selections > input {
  display: none;
}

.v-input.lang .v-input__append-inner {
  display: none;
}

/* header {
  line-height: 1.5;
  max-height: 100vh;
}

.logo {
  display: block;
  margin: 0 auto 2rem;
}

nav {
  width: 100%;
  font-size: 12px;
  text-align: center;
  margin-top: 2rem;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
}

nav a:first-of-type {
  border: 0;
}

@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }

  .logo {
    margin: 0 2rem 0 0;
  }

  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }

  nav {
    text-align: left;
    margin-left: -1rem;
    font-size: 1rem;

    padding: 1rem 0;
    margin-top: 1rem;
  }
} */
</style>
