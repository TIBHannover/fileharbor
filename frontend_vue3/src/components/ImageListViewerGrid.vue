<template>
  <div class="flex-view">
    <div
      class="grid-item"
      v-for="(entry, index) in entries"
      :style="{ height: heightString, width: widthString }"
    >
      <!-- {{ heightString }}
      {{ height }}
      {{ Number.isInteger(height) }} -->
      <!-- {{ cssItem }} -->
      <img :src="'http://localhost:8080' + entry.preview" />
    </div>
    <!-- <GridItem
      v-for="(entry, index) in pageEntries"
      :key="entry.id"
      :entry="entry"
      :isFirst="index === 0"
      :isLast="index === pageEntries.length - 1"
      :showDialog="currentDialog === entry.id"
      @next="nextEntry"
      @previous="previousEntry"
    /> -->

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
import { computed, ref, watch } from 'vue'

const probs = defineProps({
  entries: Array,
})

const height = ref(200)
const width = ref('auto')

const heightString = computed(() => {
  if (Number.isInteger(height.value)) {
    return height.value + 'px'
  } else {
    return height.value
  }
})

const widthString = computed(() => {
  if (Number.isInteger(width.value)) {
    return width.value + 'px'
  } else {
    return width.value
  }
})
</script>

<style>
.grid-item {
  border-radius: 2px;
  position: relative;
  overflow: hidden;
  min-width: 80px;
  display: block;
  flex-grow: 1;
  margin: 2px;
}

.grid-item[disabled] {
  display: none;
}

.grid-item i {
  text-shadow: 0 0 5px black;
}

.grid-item > .bookmark {
  transition: opacity 0.25s ease;
  position: absolute;
  padding: 5px;
  right: 0;
  top: 0;
}

.grid-item > .bookmark button {
  opacity: 0;
}

.grid-item > .bookmark button.clicked,
.grid-item:hover > .bookmark button {
  opacity: 1;
}

.grid-item > img {
  transition: transform 0.5s ease;
  transform: scale(1.05);
  object-fit: cover;
  min-width: 100%;
  max-width: 100%;
  height: 100%;
  opacity: 1;
}

.grid-item:hover > img {
  transform: scale(1.4);
}

.grid-item:hover > .overlay {
  opacity: 1;
}

.grid-item > .overlay {
  background: linear-gradient(to top, black, #00000000 50%);
  transform: translate(-50%, -50%);
  transition: opacity 0.25s ease;
  position: absolute;
  object-fit: cover;
  min-width: 100%;
  max-width: 100%;
  color: #ffffff;
  height: 100%;
  opacity: 0;
  left: 50%;
  top: 50%;
}

.grid-item > .overlay .view {
  padding: 5px 35px 0 0;
  text-align: right;
}

.grid-item > .overlay .meta {
  position: absolute;
  padding: 5px 10px;
  width: 100%;
  bottom: 0;
  left: 0;
}

.grid-item > .overlay .meta * {
  text-transform: capitalize;
  text-overflow: ellipsis;
  line-height: 1.35rem;
  white-space: nowrap;
  overflow: hidden;
  font-weight: 400;
}

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
