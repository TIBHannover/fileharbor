<template>
  <SearchDrawer
    :model-value="drawer"
    :data="aggregations"
    @apply="onFilter"
  />

  <v-main class="w-100">
    <div :class="['mb-3', drawer ? 'px-4' : 'px-3']">
      <SearchToolbar
        :key="toolbarKey"
        :search-results="entries.length || 0"
        :items-per-page="itemsPerPage"
        :order-by="grouping.orderBy"
        :sort-order="grouping.sortOrder"
        :view-mode="grouping.viewMode"
        @apply-group-by="onGroupBy"
        @apply-page-change="onPageChange"
      />

      <v-container
        class="overflow-y-auto"
        style="height: calc(100vh - 140px);"
        fluid
      >
        <ListIterator
          v-if="grouping.viewMode === '1d'"
          :entries="paginatedEntries"
          :items-per-page="itemsPerPage"
          :items-per-row="itemsPerRow"
        />

        <CanvasIterator
          v-if="grouping.viewMode === '2d'"
          :entries="entries"
        />
      </v-container>
    </div>
  </v-main>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useSearchStore } from '@/stores/search'
import useDisplayItems from '@/composables/useDisplayItems'
import SearchDrawer from '@/components/drawers/SearchDrawer.vue'
import SearchToolbar from '@/components/toolbars/SearchToolbar.vue'
import ListIterator from '@/components/iterators/ListIterator.vue'
import CanvasIterator from '@/components/iterators/CanvasIterator.vue'

defineProps({
  drawer: {
    type: Boolean,
    default: true
  }
})

const search = useSearchStore()
const { entries, aggregations } = storeToRefs(search)
const { itemsPerPage, itemsPerRow } = useDisplayItems('search')

const page = ref(1)

const onFilter = (payload) => {
  // TODO: add params
  console.log(payload)
  search.post()
  page.value = 1
}

const onPageChange = (newPage) => {
  page.value = newPage
}

const paginatedEntries = computed(() => {
  const entries = orderedEntries.value ?? []
  const itemsPer = itemsPerPage.value || entries.length || 1

  const totalPages = Math.max(1, Math.ceil(entries.length / itemsPer))
  const currentPage = Math.min(page.value, totalPages)

  const startIndex = (currentPage - 1) * itemsPer
  return entries.slice(startIndex, startIndex + itemsPer)
})

const grouping = ref({
  orderBy: 'relevance',
  sortOrder: 'desc',
  viewMode: '2d'
})

const onGroupBy = (payload) => {
  console.log(payload)
  grouping.value = {
    orderBy: payload.orderBy ?? 'relevance',
    sortOrder: payload.sortOrder ?? 'desc',
    viewMode: payload.viewMode ?? '1d'
  }
}

const collator = new Intl.Collator(undefined, { sensitivity: 'base', numeric: true })

function indexMeta(meta = []) {
  const map = new Map()
  for (const m of meta) {
    if (!m || !m.name) continue
    if (typeof m.value_int === 'number') map.set(m.name, m.value_int)
    else if (m.value_str != null) map.set(m.name, m.value_str)
    else map.set(m.name, null)
  }
  return map
}

function compareNullable(a, b, dir, type) {
  const an = a == null, bn = b == null
  if (an && bn) return 0
  if (an) return 1
  if (bn) return -1
  if (type === 'number') return (a - b) * dir
  return collator.compare(String(a), String(b)) * dir
}

const orderedEntries = computed(() => {
  const src = entries.value
  if (!Array.isArray(src) || !src.length) return []

  const { orderBy, sortOrder } = grouping.value
  const dir = sortOrder === 'desc' ? -1 : 1

  if (orderBy === 'relevance') {
    return sortOrder === 'asc' ? [...src].reverse() : [...src]
  }

  const decorated = src.map((e) => {
    const meta = indexMeta(e.meta)
    return {
      entry: e,
      year: meta.get('year_min') ?? null,
      title: meta.get('title') ?? null,
      id: String(e?.id ?? '')
    }
  })

  decorated.sort((a, b) => {
    if (orderBy === 'creation-date') {
      const byYear = compareNullable(a.year, b.year, dir, 'number')
      if (byYear !== 0) return byYear
    } else if (orderBy === 'object-title') {
      const byTitle = compareNullable(a.title, b.title, dir, 'string')
      if (byTitle !== 0) return byTitle
    }
    return collator.compare(a.id, b.id)
  })

  return decorated.map(d => d.entry)
})

const generateHash = (string) => {
  let h = 0
  for (const char of string) {
    h = (h << 5) - h + char.charCodeAt(0)
    h |= 0
  }
  return h
}

const toolbarKey = computed(() => {
  const sig = entries.value.map(e => e.id).join('|')
  return generateHash(sig)
})

// TODO: Remove in production
onMounted(() => {
  search.post()
})
</script>