<template>
  <v-menu
    v-model="dialog"
    id="modal-layout"
    :close-on-content-click="false"
    min-width="300"
    max-width="300"
    offset-y
    bottom
    right
    open-on-hover
  >
    <template v-slot:activator="{ on }">
      <v-btn
        v-on="on"
        text
        block
      >
        <v-icon
          color="grey darken-1"
          class="mr-2 ml-n1"
        >
          mdi-view-dashboard-outline
        </v-icon>
        <v-badge
          v-if="!defaultLayout"
          color="accent"
          :icon="layoutIcon"
        >
          <span style="font-size: 14px">
            {{ $t("modal.layout.title") }}
          </span>
        </v-badge>
        <span
          v-else
          style="font-size: 14px"
        >
          {{ $t("modal.layout.title") }}
        </span>
      </v-btn>
    </template>

    <v-card
      id="layout"
      width="300"
    >
      <v-card-text class="px-6 pt-4 pb-5">
        <v-select
          v-model="view.default"
          :items="view.items"
          class="mb-0"
          item-value="key"
          item-text="name"
          attach="#layout"
          solo
          flat
          dense
          hide-details
          @change="update"
        >
          <template v-slot:prepend>
            {{ $t("field.use") }}
          </template>

          <template v-slot:append-outer>
            <v-btn
              v-if="view.grid"
              class="ml-2"
              @click="changeViewGrid(false)"
              :title="$t('modal.layout.view.grid.hide')"
              icon
              small
            >
              <v-icon>mdi-grid-off</v-icon>
            </v-btn>
            <v-btn
              v-else
              class="ml-2"
              @click="changeViewGrid(true)"
              :title="$t('modal.layout.view.grid.show')"
              icon
              small
            >
              <v-icon>mdi-grid</v-icon>
            </v-btn>
          </template>
        </v-select>

        <v-select
          v-model="sort.default"
          :items="sort.items"
          class="mb-2"
          item-value="key"
          item-text="name"
          attach="#layout"
          solo
          flat
          dense
          hide-details
          @change="update"
        >
          <template v-slot:prepend>
            {{ $t("modal.layout.sort.title") }}
          </template>

          <template v-slot:append-outer>
            <v-btn
              v-if="sort.order === 'desc'"
              class="ml-2"
              @click="changeSortOrder('asc')"
              :title="$t('modal.layout.sort.order.asc')"
              icon
              small
            >
              <v-icon>mdi-sort-ascending</v-icon>
            </v-btn>
            <v-btn
              v-else
              class="ml-2"
              @click="changeSortOrder('desc')"
              :title="$t('modal.layout.sort.order.desc')"
              icon
              small
            >
              <v-icon>mdi-sort-descending</v-icon>
            </v-btn>
          </template>
        </v-select>

        <div :title="$t('modal.layout.itemSize')">
          <v-slider
            v-model="itemSize"
            min="-7"
            max="7"
            color="secondary"
            :disabled="view.default === 'umap' && view.grid"
            prepend-icon="mdi-magnify-scan"
            hide-details
            @end="update"
          >
            <template v-slot:append>
              <v-text-field
                v-model="itemSize"
                type="number"
                class="mt-0 pt-0"
                background-color="grey lighten-4"
                style="width: 80px"
                hide-details
                single-line
                rounded
                flat
              ></v-text-field>
            </template>
          </v-slider>
        </div>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import { isMobile } from '@/plugins/helpers';

export default {
  data() {
    return {
      dialog: false,
      itemSize: 0,
      view: {
        default: 'flexible',
        grid: false,
        items: [
          { key: 'flexible', name: this.$t('modal.layout.view.type.flexible'), disabled: false },
          { key: 'umap', name: this.$t('modal.layout.view.type.umap'), disabled: false },
        ],
      },
      sort: {
        default: 'relevance',
        order: 'asc',
        items: [
          { key: 'relevance', name: this.$t('modal.layout.sort.type.relevance') },
          { key: 'title', name: this.$t('modal.layout.sort.type.title') },
          { key: 'date', name: this.$t('modal.layout.sort.type.date') },
        ],
      },
    };
  },
  props: ['values'],
  methods: {
    update() {
      const values = {
        itemSize: this.itemSize,
        sortOrder: this.sort.order,
        sortType: this.sort.default,
        viewGrid: this.view.grid,
        viewType: this.view.default,
      };
      this.$emit('update', values);
    },
    change() {
      if (this.values && Object.keys(this.values).length) {
        if (this.keyInObj('itemSize', this.values)) {
          this.itemSize = this.values.itemSize;
        }
        if (this.keyInObj('viewGrid', this.values)) {
          this.view.grid = this.values.viewGrid;
        }
        if (this.keyInObj('viewType', this.values)) {
          this.view.default = this.values.viewType;
        }
        if (this.keyInObj('sortOrder', this.values)) {
          this.sort.order = this.values.sortOrder;
        }
        if (this.keyInObj('sortType', this.values)) {
          this.sort.default = this.values.sortType;
        }
      } else {
        this.itemSize = 0;
        this.sort.order = 'asc';
        this.sort.default = 'relevance';
        this.view.grid = false;
        this.view.default = 'flexible';
      }
      this.update();
    },
    changeViewGrid(value) {
      this.view.grid = value;
      this.update();
    },
    changeSortOrder(value) {
      this.sort.order = value;
      this.update();
    },
  },
  computed: {
    toggle() {
      return this.$store.state.user.modal.layout;
    },
    reset() {
      return this.$store.state.api.settings.layout;
    },
    defaultLayout() {
      return this.sort.order === 'asc' && this.sort.default === 'relevance';
    },
    layoutIcon() {
      if (this.sort.order === 'asc') {
        switch (this.sort.default) {
          case 'title':
            return 'mdi-sort-alphabetical-ascending';
          case 'date':
            return 'mdi-sort-clock-ascending';
          default:
            return 'mdi-sort-bool-ascending';
        }
      }
      switch (this.sort.default) {
        case 'title':
          return 'mdi-sort-alphabetical-descending';
        case 'date':
          return 'mdi-sort-clock-descending';
        default:
          return 'mdi-sort-bool-descending';
      }
    },
  },
  watch: {
    toggle(value) {
      this.dialog = value;
    },
    reset(newValues, oldValues) {
      if (!this.isEqual(newValues, oldValues)) {
        this.change();
      }
    },
  },
  created() {
    this.change();
    this.view.items.forEach((item, index) => {
      if (item.key === 'umap' && isMobile()) {
        this.view.items[index].disabled = true;
      }
    });
  },
};
</script>

<style>
#layout .v-select .v-input__slot {
  padding-right: 3px !important;
  padding-left: 1px !important;
}

#layout .v-select .v-input__prepend-outer {
  display: flex;
  min-height: 27px;
  margin-right: 4px;
  align-items: center;
  white-space: nowrap;
}
</style>
