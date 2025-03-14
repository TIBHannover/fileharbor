<template>
  <v-combobox
    v-model="query"
    class="mx-1 sbar"
    @keyup.enter="submit($event, (random = false))"
    :placeholder="$t('home.search.placeholder')"
    clearable
    chips
    multiple
    variant="outlined"
    hide-details="auto"
    rounded
  >
    <template v-slot:chip="{ item, index, props }">
      <v-chip @click:close="remove(index)" close>
        <v-btn
          v-if="item.positive"
          @click="toggle(index)"
          :title="$t('home.search.query.negative')"
          class="ml-n2"
          icon
          small
        >
          <v-icon>mdi-plus</v-icon>
        </v-btn>
        <v-btn
          v-else
          @click="toggle(index)"
          :title="$t('home.search.query.positive')"
          class="ml-n2"
          icon
          small
        >
          <v-icon>mdi-minus</v-icon>
        </v-btn>

        <v-icon v-if="item.type === 'idx'" class="mr-1" style="font-size: 18px">
          mdi-file-image-outline
        </v-icon>
        <v-icon v-else class="mr-1" style="font-size: 18px"> mdi-file-document-outline </v-icon>

        <span v-if="item.type === 'idx'" :title="item.label">
          {{ item.label }}
        </span>
        <span v-else :title="item.value">
          {{ item.value }}
        </span>
      </v-chip>
    </template>
  </v-combobox>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useSearchStore } from '@/stores/search'
import { useHelper } from '@/composables/helper'

const search_store = useSearchStore()
const query = ref([{ type: 'txt', positive: true, value: 'ceiling painting' }])

const helper = useHelper()

function submit(event, random = false) {
  console.log('SUBMIT')
  search_store.search(query.value)
}

function remove(index) {
  if (index === -1) {
    this.query = []
  } else {
    this.query.splice(index, 1)
  }
}
function toggle(index) {
  const { positive } = this.query[index]
  this.query[index].positive = !positive
}
watch(
  query,
  async (n, o) => {
    if (!helper.isEqual(n, o)) {
      let new_query = []
      n.every((value) => {
        if (typeof value === 'string') {
          let positive = true
          if (value.charAt(0) === '-') {
            value = value.slice(1)
            positive = false
          }
          new_query.push({ type: 'txt', positive, value })
        } else if (typeof value === 'object') {
          if (value.example) {
            query = value.entries
            return false
          }
          new_query.push(value)
        }
        return true
      })
      query.value = new_query
    }
  },
  { deep: true },
)
</script>

<style>
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
</style>
