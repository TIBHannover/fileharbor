<template>
  <v-navigation-drawer
    v-model="drawer"
    class="filters"
    width="350"
    style="padding-bottom: 100px;"
    app
    right
    hide-overlay
    disable-resize-watcher
  >
    <v-toolbar
      flat
      class="v-bar--underline"
    >
      <v-toolbar-title>{{ $t("drawer.filter.title") }}</v-toolbar-title>

      <div class="v-btn--absolute v-btn--right">
        <span v-if="loggedIn">
          <v-btn
            v-if="toggleBookmarks"
            @click="toggleBookmarks = false"
            :title="$t('drawer.filter.bookmarks.hide')"
            icon
          >
            <v-icon>mdi-bookmark-off-outline</v-icon>
          </v-btn>
          <v-btn
            v-else
            @click="toggleBookmarks = true"
            :title="$t('drawer.filter.bookmarks.show')"
            icon
          >
            <v-icon>mdi-bookmark-outline</v-icon>
          </v-btn>
        </span>

        <v-btn
          :title="$t('drawer.filter.remove')"
          @click="removeAllFilters"
          class="ml-n4"
          icon
        >
          <v-icon>mdi-trash-can-outline</v-icon>
        </v-btn>

        <v-btn
          @click="close"
          class="ml-n2"
          icon
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </div>
    </v-toolbar>

    <v-container class="ml-1 mt-n1">
      <div>
        <label
          v-if="fullText.length"
          class="v-label v-label--active theme--light ml-6"
        >
          {{ $t("drawer.filter.field")["full.text"] }}
        </label>

        <v-combobox
          v-model="fullText"
          :label="$t('drawer.filter.field')['full.text']"
          background-color="grey lighten-4"
          class="mb-4"
          rounded
          hide-details
          flat
          clearable
          multiple
          solo
          chips
          deletable-chips
        ></v-combobox>
      </div>

      <div
        v-for="(count, index) in counts"
        :key="index"
      >
        <label
          v-if="notEmpty(count.field)"
          class="v-label v-label--active theme--light ml-6"
        >
          {{ $t("drawer.filter.field")[count.field] }}
        </label>

        <v-combobox
          v-model="data[count.field]"
          item-value="name"
          :items="count.entries"
          :disabled="!count.entries.length"
          background-color="grey lighten-4"
          :filter="filterAutocomplete"
          @click:clear="remove(-1, count.field)"
          :label="$t('drawer.filter.field')[count.field]"
          class="mb-4"
          solo
          rounded
          hide-details
          hide-selected
          flat
          clearable
          multiple
          @change="change"
        >
          <template v-slot:item="{ on, item }">
            <v-list-item v-on="on">
              <v-list-item-content>
                <v-list-item-title :class="'meta ' + count.field.replace('.', '-')">
                  <div :title="item.name">{{ item.name }}</div>
                  <div
                    class="ml-3"
                    :title="item.count + ' ' + $t('drawer.filter.objects')"
                  >
                    ({{ item.count }})
                  </div>
                </v-list-item-title>
              </v-list-item-content>
            </v-list-item>
          </template>

          <template v-slot:selection="{ attrs, selected, item, index }">
            <v-chip
              v-bind="attrs"
              :input-value="selected"
              @click:close="remove(index, count.field)"
              close
              :class="count.field.replace('.', '-')"
            >
              <v-btn
                v-if="data[count.field][index].positive"
                @click="toggle(index, count.field)"
                :title="$t('drawer.filter.query.negative')"
                font-size="18"
                class="ml-n2"
                icon
                small
              >
                <v-icon>mdi-plus</v-icon>
              </v-btn>
              <v-btn
                v-else
                @click="toggle(index, count.field)"
                :title="$t('drawer.filter.query.positive')"
                font-size="18"
                class="ml-n2"
                icon
                small
              >
                <v-icon>mdi-minus</v-icon>
              </v-btn>

              <span :title="item.name">{{ item.name }}</span>
            </v-chip>

            <v-spacer />
          </template>
        </v-combobox>
      </div>

      <div class="date-range mb-4">
        <v-layout
          row
          class="mx-6 ma-1"
        >
          <label class="v-input v-label v-label--active theme--light">
            {{ $t("drawer.filter.field['meta.period']") }}
          </label>

          <v-btn
            v-if="dateToggle"
            @click="dateToggle = false"
            :title="$t('drawer.filter.period.hide')"
            icon
            small
          >
            <v-icon>mdi-eye-off-outline</v-icon>
          </v-btn>
          <v-btn
            v-else
            @click="dateToggle = true"
            :title="$t('drawer.filter.period.show')"
            icon
            small
          >
            <v-icon>mdi-eye-outline</v-icon>
          </v-btn>
        </v-layout>

        <v-range-slider
          v-if="dateToggle"
          v-model="dateRange"
          min="1000"
          max="2000"
          color="secondary"
          :disabled="!dateToggle"
          @end="commitDateRange"
          hide-details
        >
          <template v-slot:prepend>
            <v-text-field
              :value="dateRange[0]"
              type="number"
              class="mt-0 pt-0"
              background-color="grey lighten-4"
              style="width: 85px"
              @change="$set(dateRange, 0, $event)"
              hide-details
              single-line
              rounded
              flat
            />
          </template>

          <template v-slot:append>
            <v-text-field
              :value="dateRange[1]"
              type="number"
              class="mt-0 pt-0"
              background-color="grey lighten-4"
              style="width: 85px"
              @change="$set(dateRange, 1, $event)"
              hide-details
              single-line
              rounded
              flat
            />
          </template>
        </v-range-slider>
      </div>
    </v-container>
  </v-navigation-drawer>
</template>

<script>
export default {
  data() {
    return {
      data: {},
      fullText: this.$store.state.api.fullText,
      dateToggle: false,
      dateRange: [1400, 1900],
      drawer: this.$store.state.user.drawer.filter,
      toggleBookmarks: this.$store.state.bookmark.toggle,
    };
  },
  methods: {
    close() {
      this.$store.commit('user/toggleDrawer', 'filter');
    },
    change() {
      Object.keys(this.data).forEach((field) => {
        this.data[field] = this.data[field].map((name) => {
          if (typeof name === 'string') {
            let positive = true;
            if (name.charAt(0) === '-') {
              name = name.slice(1);
              positive = false;
            }
            name = { positive, name };
          } else if (
            typeof name === 'object'
            && !this.keyInObj('positive', name)
          ) {
            name = { positive: true, ...name };
          }
          return name;
        });
      });
      this.$store.commit('api/updateFilters', this.data);
    },
    remove(index, field) {
      if (index === -1) {
        this.data[field] = [];
      } else {
        this.data[field].splice(index, 1);
      }
    },
    toggle(index, field) {
      const value = this.data[field][index].positive;
      this.data[field][index].positive = !value;
    },
    removeAllFilters() {
      this.$store.commit('api/removeAllFilters');
    },
    commitDateRange() {
      this.$store.commit('api/updateDateRange', this.dateRange);
    },
    filterAutocomplete(item, queryText) {
      const key = item.name.toLocaleLowerCase();
      const query = queryText.toLocaleLowerCase();
      return key.indexOf(query) > -1;
    },
    notEmpty(field) {
      if (Object.prototype.hasOwnProperty.call(this.data, field)) {
        if (this.data[field].length) {
          return true;
        }
      }
      return false;
    },
  },
  computed: {
    counts() {
      return this.$store.state.api.counts;
    },
    filters() {
      return this.$store.state.api.filters;
    },
    toggleDrawer() {
      return this.$store.state.user.drawer.filter;
    },
    updateDateToggle() {
      return this.$store.state.api.dateRange.length;
    },
    updateFullText() {
      return this.$store.state.api.fullText;
    },
    loggedIn() {
      return this.$store.state.user.loggedIn;
    },
  },
  watch: {
    counts: {
      handler(counts) {
        counts.forEach(({ field, entries }) => {
          if (field === 'collection' && this.data.collection) {
            const mapper = entries.reduce((obj, x) => ({...obj, [x.hash_id]: x}), {});
            this.data.collection.forEach((selection, i) => {
              const name = mapper[selection.hash_id].name;
              this.data.collection[i].name = name;
            });
          }
        });
      },
      deep: true,
    },
    filters: {
      handler(filter) {
        this.data = { ...filter };
      },
      deep: true,
      immediate: true,
    },
    drawer(value) {
      if (!value && this.$store.state.user.drawer.filter) {
        this.$store.commit('user/toggleDrawer', 'filter');
      }
    },
    toggleDrawer(value) {
      this.drawer = value;
    },
    toggleBookmarks(value) {
      this.$store.commit('bookmark/update', value);
    },
    dateToggle(value) {
      if (value) {
        this.$store.commit('api/updateDateRange', this.dateRange);
      } else {
        this.$store.commit('api/updateDateRange', []);
      }
    },
    updateDateToggle(value) {
      if (value === 0) {
        this.dateToggle = false;
      }
    },
    fullText() {
      this.$store.commit('api/updateFullText', this.fullText);
    },
    updateFullText(value) {
      this.fullText = value;
    },
  },
  created() {
    const { dateRange } = this.$store.state.api;
    if (dateRange.length) {
      this.dateRange = dateRange;
      this.dateToggle = true;
    }
  },
};
</script>

<style>
.v-navigation-drawer:not(.v-navigation-drawer--close) {
  box-shadow: 0 8px 10px -5px rgb(0 0 0 / 20%), 0 16px 24px 2px rgb(0 0 0 / 14%),
    0 6px 30px 5px rgb(0 0 0 / 12%);
}

.container > div > label {
  font-size: 12px;
}

.date-range .row > label {
  align-items: center;
  font-size: 12px;
}

.v-select__slot .v-chip__content > span {
  text-overflow: ellipsis;
  max-width: 150px;
  overflow: hidden;
}

.v-select__selections {
  margin: 4px 0;
}

.filters .spacer {
  width: 100%;
}

.filters .spacer:nth-last-child(2) {
  display: none;
}

.v-menu__content {
  background-color: #fff;
}

.v-menu__content .v-list-item__title {
  display: flex;
  line-height: 1.5;
  white-space: inherit;
}

.v-menu__content .v-list-item__title.meta > div:first-child {
  max-width: 200px;
}

.v-menu__content .v-list-item__title.meta > div:last-child {
  text-align: right;
  flex-grow: 1;
  color: #bbb;
}

input::-webkit-outer-spin-button,
input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

.v-select__slot label,
.container > div > label,
.v-autocomplete__content .meta.origin-name,
.v-autocomplete .v-chip.origin-name {
  text-transform: capitalize;
}
</style>
