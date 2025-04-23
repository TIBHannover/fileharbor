<template>
  <div class="grid-item" :style="{ height: heightString, width: widthString }">
    <img :src="'http://localhost:8080' + entry.preview" />

    <!-- <ImageItemModal v-model="dialog" :entry="entry" /> -->

    <div class="overlay">
      <div class="view">
        <v-menu offset-y bottom right>
          <template v-slot:activator="{ attrs, on: menu }">
            <v-btn :title="$t('search.object')" v-bind="attrs" v-on="menu" icon variant="text">
              <v-icon color="white" class="shadow"> mdi-magnify </v-icon>
            </v-btn>
          </template>

          <v-list class="pa-0">
            <v-list-item @click="query(false)">
              {{ $t('search.new') }}
            </v-list-item>

            <v-list-item @click="query(true)">
              {{ $t('search.append') }}
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <div class="meta">
        <div class="text-subtitle-1" :title="title">
          {{ title }}
        </div>

        <div class="text-caption" :title="artist">
          {{ artist }}
        </div>
      </div>
    </div>

    <div class="bookmark">
      <v-btn v-if="bookmarked" @click="bookmark" class="ml-n1 clicked" icon variant="text">
        <v-icon :title="$t('griditem.bookmark.remove')" color="accent" class="shadow">
          mdi-bookmark-remove-outline
        </v-icon>
      </v-btn>

      <v-btn v-else @click="bookmark" class="ml-n1" icon variant="text">
        <v-icon color="white" class="shadow" :title="$t('griditem.bookmark.add')">
          mdi-bookmark-outline
        </v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script setup>
import ImageItemModal from '@/components/ImageItemModal.vue'
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
const { t } = useI18n()

const props = defineProps({
  entry: Object,
})

const dialog = ref(false)

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

const title = computed(() => {
  const title = []
  props.entry.meta.forEach(({ name, value_str }) => {
    if (name === 'title' && value_str) {
      title.push(value_str)
    }
  })
  if (title.length) return title[0]
  return t('griditem.notitle')
})
const artist = computed(() => {
  const artist = []
  props.entry.meta.forEach(({ name, value_str }) => {
    if (name === 'artist_name' && value_str) {
      artist.push(value_str)
    }
  })
  if (artist.length) return artist.join(', ')
  return t('griditem.noartist')
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
