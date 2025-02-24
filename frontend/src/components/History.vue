<template>
  <v-menu
    v-model="menu"
    min-width="365"
    max-width="365"
    max-height="600"
    offset-y
    bottom
    left
    open-on-hover
    :close-on-content-click="false"
  >
    <template v-slot:activator="{ attrs, on: menu }">
      <v-btn
        icon
        v-bind="attrs"
        v-on="menu"
        class="ml-n2"
        :title="$t('drawer.history.title')"
      >
        <v-badge
          v-if="data.length"
          color="accent"
          :content="data.length"
        >
          <v-icon>mdi-history</v-icon>
        </v-badge>
        <v-icon v-else>mdi-history</v-icon>
      </v-btn>
    </template>

    <v-list
      class="pa-0 history"
      v-if="data.length"
    >
      <v-row
        class="ma-0"
        align-content="center"
        style="border-bottom: 1px solid #f5f5f5;"
      >
        <v-col
          cols="auto"
          class="v-menu__title mx-1"
        >
          {{ $t('drawer.history.title') }}
        </v-col>

        <v-spacer />

        <v-col cols="2">
          <v-layout justify-end>
            <v-btn
              :title="$t('drawer.history.remove')"
              class="ml-n2"
              @click="removeAllItems"
              icon
            >
              <v-icon>mdi-trash-can-outline</v-icon>
            </v-btn>
          </v-layout>
        </v-col>
      </v-row>

      <v-list-item-group>
        <v-list-item
          v-for="(item, index) in data"
          :key="index"
        >
          <v-list-item-content @click="submit(item, ...arguments)">
            <div class="query">
              <span
                :title="title(item)"
                class="clip mr-1"
              >{{ title(item) }}</span>
              <span class="v-label theme--light"> · {{ date(item) }}</span>
            </div>

            <div
              :title="filters(item)"
              class="clip"
            >
              <v-icon
                size="12"
                class="mr-2"
                small
              >mdi-tune</v-icon>
              <span style="font-size: 12px;">{{ filters(item) }}</span>
            </div>

            <v-btn
              @click="removeItem(item)"
              :title="$t('button.remove')"
              style="justify-content: center;"
              icon
              absolute
              right
            >
              <v-icon small>mdi-trash-can-outline</v-icon>
            </v-btn>
          </v-list-item-content>
        </v-list-item>
      </v-list-item-group>
    </v-list>
  </v-menu>
</template>

<script>
export default {
  data() {
    return {
      menu: false,
    };
  },
  methods: {
    title(item) {
      if (item.random) {
        return this.$t('search.random');
      }
      if (item.query.length) {
        const title = this.$t('drawer.history.query.filled');
        const values = [];
        item.query.forEach(({ value, label }) => {
          if (label) {
            values.push(label);
          } else {
            values.push(value);
          }
        });
        return `${title}: ${values.join(', ')}`;
      }
      return this.$t('drawer.history.query.empty');
    },
    date(item) {
      const date = new Date(item.date);
      const hours = date.getHours();
      const minutes = date.getMinutes();
      if (date.setHours(0, 0, 0, 0) === (new Date()).setHours(0, 0, 0, 0)) {
        if (minutes < 10) {
          return `${hours}:0${minutes}`;
        }
        return `${hours}:${minutes}`;
      }
      const month = date.toLocaleString('default', { month: 'short' });
      if (navigator.language.startsWith('en-')) {
        return `${month}, ${date.getDate()}`;
      }
      return `${date.getDate()}. ${month}`;
    },
    filters(item) {
      const values = [];
      if (item.full_text && item.full_text.length) {
        const title = this.$t('drawer.filter.field')['full.text'];
        values.push(`${title}: ${item.full_text.join(', ')}`);
      }
      if (item.filters && Object.keys(item.filters).length) {
        Object.keys(item.filters).forEach((field) => {
          if (item.filters[field].length) {
            const title = this.$t('drawer.filter.field')[field];
            const value = item.filters[field].map((n) => {
              if (!n.positive) return `–${n.name}`;
              return n.name;
            });
            values.push(`${title}: ${value.join(', ')}`);
          }
        });
      }
      if (item.date_range && item.date_range.length) {
        const title = this.$t('drawer.filter.field')['meta.period'];
        values.push(`${title}: ${item.date_range.join('–')}`);
      }
      if (values.length) return `${values.join(' · ')}`;
      return this.$t('drawer.history.filter.empty');
    },
    removeItem(item) {
      this.$store.commit('bookmark/removeHistory', item);
    },
    removeAllItems() {
      this.$store.commit('bookmark/removeAllHistory');
    },
    submit(item, event) {
      if (event.target.nodeName !== 'I') {
        this.$store.commit('api/updateAll', item);
      }
    },
  },
  computed: {
    data() {
      return this.$store.state.bookmark.history.slice(1);
    },
  },
};
</script>

<style scoped>
.v-menu__content:empty {
  box-shadow: none;
}

.v-menu__content .clip {
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
}

.v-menu__content span.clip {
  max-width: 190px;
}

.v-menu__title {
  display: flex;
  align-items: center;
  font-size: 1.25rem;
}

.history .v-list-item__content>button {
  opacity: 0;
}

.history .v-list-item__content:hover>button {
  opacity: 1;
}

.history .v-list-item__content .query {
  line-height: 1.25;
}

.history .v-list-item__content .query>span {
  display: inline-block;
  vertical-align: middle;
  max-width: 210px;
}

.v-menu__content .history .v-btn:not(.accent) {
  justify-content: center;
}
</style>
