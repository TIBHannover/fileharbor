<template>
  <v-combobox
    v-model="queries"
    class="mx-1 sbar"
    :placeholder="$t('home.search.placeholder')"
    clearable
    chips
    multiple
    variant="outlined"
    hide-details="auto"
    rounded
    @keyup.enter="submit()"
  >
    <template #chip="{ item, index }">
      <v-chip
        close
        @click:close="remove(index)"
      >
        <v-btn
          v-if="item.positive"
          :title="$t('home.search.query.negative')"
          class="ml-n2"
          icon
          small
          @click="toggle(index)"
        >
          <v-icon>mdi-plus</v-icon>
        </v-btn>
        <v-btn
          v-else
          :title="$t('home.search.query.positive')"
          class="ml-n2"
          icon
          small
          @click="toggle(index)"
        >
          <v-icon>mdi-minus</v-icon>
        </v-btn>

        <v-icon
          v-if="item.type === 'idx'"
          class="mr-1"
          style="font-size: 18px"
        >
          mdi-file-image-outline
        </v-icon>
        <v-icon
          v-else
          class="mr-1"
          style="font-size: 18px"
        >
          mdi-file-document-outline
        </v-icon>

        <span
          v-if="item.type === 'idx'"
          :title="item.label"
        >
          {{ item.label }}
        </span>
        <span
          v-else
          :title="item.value"
        >
          {{ item.value }}
        </span>
      </v-chip>
    </template>
  </v-combobox>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useSearchStore } from '@/stores/search'
import isEqual from '@/composables/useIsEqual'

const searchStore = useSearchStore()

let queries = ref([{ type: 'txt', positive: true, value: 'ceiling painting' }])

function submit() {
  console.log('SUBMIT')
  searchStore.setQueries(queries.value)
  searchStore.search()
}

function remove(index) {
  if (index === -1) {
    this.queries = []
  } else {
    this.queries.splice(index, 1)
  }
}
function toggle(index) {
  const { positive } = this.queries[index]
  this.queries[index].positive = !positive
}
watch(
  queries,
  async (n, o) => {
    if (!isEqual(n, o)) {
      let new_queries = []
      n.every((value) => {
        if (typeof value === 'string') {
          let positive = true
          if (value.charAt(0) === '-') {
            value = value.slice(1)
            positive = false
          }
          new_queries.push({ type: 'txt', positive, value })
        } else if (typeof value === 'object') {
          if (value.example) {
            queries.value = value.entries
            return false
          }
          new_queries.push(value)
        }
        return true
      })
      queries.value = new_queries
    }
  },
  { deep: true },
)
</script>

<style>
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

.v-input.lang > .v-input__control .v-select__selections > input {
  display: none;
}

header .v-autocomplete .v-text-field.v-text-field--solo .v-input__control input {
  max-width: fit-content;
  min-width: 0;
}

header .v-text-field--outlined.v-input--has-state fieldset,
header .v-text-field--outlined.v-input--is-focused fieldset {
  border: 0 solid;
}

header .v-text-field--filled > .v-input__control > .v-input__slot,
header .v-text-field--full-width > .v-input__control > .v-input__slot,
header .v-text-field--outlined > .v-input__control > .v-input__slot {
  min-height: 48px;
}

.v-main .v-text-field--outlined.v-input--has-state fieldset,
.v-main .v-text-field--outlined.v-input--is-focused fieldset {
  border: 3px solid;
}

header .theme--light.v-text-field--outlined:not(.v-input--is-focused, .v-input--has-state) > .v-input__control > .v-input__slot fieldset {
  border: 0 solid;
}

.v-chip .v-avatar {
  padding-top: 3px;
}

.v-chip__content .v-btn__content {
  justify-content: center;
}

.v-input .v-btn {
  letter-spacing: 1;
}

.v-input.lang {
  font-family: 'Roboto Mono', monospace;
  text-transform: uppercase;
  width: min-content;
}

.v-input.lang > .v-input__control > .v-input__slot {
  padding: 0 6px !important;
}

.theme--light.v-icon,
.v-dialog .v-expansion-panel-content__wrap .capitalize {
  color: rgb(69 123 157 / 54%);
}

.v-input.lang .v-input__append-inner {
  display: none;
}

.v-input__prepend-inner .theme--light.v-icon,
.v-input__icon--append .theme--light.v-icon:not(.mdi-menu-down) {
  color: rgb(0 0 0 / 54%);
}

.v-application--is-ltr .v-text-field.v-text-field .v-input__prepend-inner {
  padding-right: 12px;
}

.v-select.v-select--is-menu-active .v-input__icon--append .v-icon {
  transform: rotate(0deg);
}

.sbar.v-autocomplete .v-select__selections {
  -ms-overflow-style: none;
  scrollbar-width: none;
  flex-wrap: nowrap;
  overflow: auto hidden;
}

.sbar.v-autocomplete .v-select__selections::-webkit-scrollbar {
  height: 0;
  width: 0;
}

.sbar.v-autocomplete .v-select__selections > .v-chip {
  overflow: initial;
}

.v-main
  .theme--light.v-text-field--outlined:not(.v-input--is-focused, .v-input--has-state)
  > .v-input__control
  > .v-input__slot
  fieldset {
  border: 3px solid;
  color: #f5f5f5;
}
</style>
