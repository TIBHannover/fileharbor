<template>
  <div class="flex-view">
    <GridItem
      v-for="(entry, index) in pageEntries"
      :key="entry.id"
      :entry="entry"
      :isFirst="index === 0"
      :isLast="index === pageEntries.length - 1"
      :showDialog="currentDialog === entry.id"
      @next="nextEntry"
      @previous="previousEntry"
    />

    <div class="grid-item-fill"></div>

    <v-pagination
      v-if="nPages > 1"
      v-model="page"
      :length="nPages"
      :total-visible="6"
      class="mt-4"
      color="accent"
      circle
    />
  </div>
</template>

<script>
import GridItem from '@/components/GridItem.vue';

export default {
  props: ['entries'],
  data() {
    return {
      page: 1,
      perPage: 150,
      currentDialog: null,
    };
  },
  methods: {
    nextEntry(entry) {
      const index = this.pageEntries.indexOf(entry);
      if (index + 1 < this.pageEntries.length) {
        const entry = this.pageEntries[index + 1];
        this.currentDialog = entry.id;
      }
    },
    previousEntry(entry) {
      const index = this.pageEntries.indexOf(entry);
      if (index > 0) {
        const entry = this.pageEntries[index - 1];
        this.currentDialog = entry.id;
      }
    },
  },
  computed: {
    nPages() {
      return Math.ceil(this.entries.length / this.perPage);
    },
    pageEntries() {
      const firstEntry = (this.page - 1) * this.perPage;
      const lastEntry = firstEntry + this.perPage;
      return this.entries.slice(firstEntry, lastEntry);
    },
  },
  watch: {
    entries() {
      this.page = 1;
    },
    page() {
      window.scrollTo(0, 0);
    },
  },
  components: {
    GridItem,
  },
};
</script>

<style>
.flex-view {
  flex-grow: 1;
  display: flex;
  flex-wrap: wrap;
  overflow: hidden;
  transition: flex-basis 0.2s ease;
}

.flex-view:after {
  content: "";
  flex: auto;
}

.grid-item-fill {
  flex-grow: 150;
}

nav[role=navigation] {
  text-align: center;
  width: 100%;
}

nav[role=navigation] button {
  box-shadow: none;
}

nav[role=navigation] button:focus {
  outline: none;
}

.theme--light.v-pagination .v-pagination__item--active.accent {
  color: #fff !important;
}
</style>
