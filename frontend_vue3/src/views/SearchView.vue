<template>
  <SearchDrawer
    :model-value="drawer"
    :data="aggregations"
    @apply="onFilter"
  />

  <v-main>
    <div :class="drawer ? 'mx-4' : 'mx-3'">
      <SearchToolbar
        :count="entries.length || 0"
        @apply="onGroupBy"
      />

      <v-container
        class="overflow-y-auto"
        style="max-height: calc(100vh - (64px + 56px));"
        fluid
      >
        <v-data-iterator
          :items="entries || []"
          :items-per-page="itemsPerPage"
          hide-default-footer
        >
          <template #default="{ items }">
            <v-row>
              <v-col
                v-for="item in items"
                :key="item.raw.id"
                :cols="(12 / itemsPerRow)"
                class="pa-1"
              >
                <SearchCard :item="item.raw" />
              </v-col>
            </v-row>
          </template>

          <template #no-data />
        </v-data-iterator>
      </v-container>
    </div>
  </v-main>
</template>

<script setup>
import { onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSearchStore } from '@/stores/search'
import useDisplayItems from '@/composables/useDisplayItems'
import SearchCard from '@/components/cards/SearchCard.vue'
import SearchDrawer from '@/components/drawers/SearchDrawer.vue'
import SearchToolbar from '@/components/toolbars/SearchToolbar.vue'

const search = useSearchStore()
const { entries, aggregations } = storeToRefs(search)

defineProps({
  drawer: {
    type: Boolean,
    default: true
  }
})

const {
  itemsPerPage,
  itemsPerRow,
  noDataCols
} = useDisplayItems('search')

const onFilter = (payload) => {
  // TODO: add params
  console.log(payload)
  search.post()
}

const onGroupBy = (payload) => {
  console.log(payload)
  // TODO: reorder entries
}

// TODO: Remove in production
onMounted(() => {
  search.post()
})
</script>