<template>
  <div
    @click="showDetails"
    class="grid-item"
    :disabled="disabled"
    :title="$t('griditem.view')"
    :style="getCss"
  >
    <ModalItem
      v-model="dialog"
      @previous="previous"
      @next="next"
      :entry="entry"
      :isFirst="isFirst"
      :isLast="isLast"
    />

    <img
      :src="entry.preview"
      v-on:error="onError"
    />

    <div class="overlay">
      <div class="view">
        <v-menu
          offset-y
          bottom
          right
        >
          <template v-slot:activator="{ attrs, on: menu }">
            <v-btn
              :title="$t('search.object')"
              v-bind="attrs"
              v-on="menu"
              icon
            >
              <v-icon
                color="white"
                class="shadow"
              >
                mdi-magnify
              </v-icon>
            </v-btn>
          </template>

          <v-list class="pa-0">
            <v-list-item @click="query(false)">
              {{ $t("search.new") }}
            </v-list-item>

            <v-list-item @click="query(true)">
              {{ $t("search.append") }}
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <div class="meta">
        <div
          class="text-subtitle-1"
          :title="title"
        >
          {{ title }}
        </div>

        <div
          class="text-caption"
          :title="artist"
        >
          {{ artist }}
        </div>
      </div>
    </div>

    <div class="bookmark">
      <v-btn
        v-if="bookmarked"
        @click="bookmark"
        class="ml-n1 clicked"
        icon
      >
        <v-icon
          :title="$t('griditem.bookmark.remove')"
          color="accent"
          class="shadow"
        >
          mdi-bookmark-remove-outline
        </v-icon>
      </v-btn>

      <v-btn
        v-else
        @click="bookmark"
        class="ml-n1"
        icon
      >
        <v-icon
          color="white"
          class="shadow"
          :title="$t('griditem.bookmark.add')"
        >
          mdi-bookmark-outline
        </v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script>
import ModalItem from '@/components/ModalItem.vue';

export default {
  props: {
    entry: Object,
    isFirst: Boolean,
    isLast: Boolean,
    showDialog: Boolean,
  },
  data() {
    return {
      width: 'auto',
      dialog: false,
      height: '200px',
      disabled: false,
      bookmarked: false,
    };
  },
  methods: {
    query(append) {
      const query = {
        type: 'idx',
        positive: true,
        value: this.entry.id,
        weights: {},
        roi: null,
        label: this.title,
        preview: this.entry.preview,
      };
      if (append) {
        this.$store.commit('api/addQuery', query);
      } else {
        this.$store.commit('api/updateQuery', [query]);
        this.$store.commit('api/removeAllFilters');
      }
      this.$store.commit('api/updateRandom', false);
    },
    bookmark(event) {
      if (event.target.nodeName === 'I') {
        if (!this.bookmarked) {
          this.$store.dispatch('bookmark/add', { id: this.entry.id });
        } else {
          this.$store.dispatch('bookmark/remove', { id: this.entry.id });
        }
        this.bookmarked = !this.bookmarked;
      }
    },
    showDetails(event) {
      if (event.target.nodeName !== 'I') {
        this.dialog = true;
      }
    },
    onError() {
      this.disabled = true;
    },
    updateSize() {
      if (Object.keys(this.settings).length) {
        const pixels = this.settings.layout.itemSize * 25;
        if (!this.settings.layout.viewGrid) {
          this.height = `${200 + pixels}px`;
          this.width = 'auto';
        } else {
          this.height = `${200 + pixels}px`;
          this.width = `${200 + pixels}px`;
        }
      }
    },
    isBookmarked() {
      const { history } = this.$store.state.bookmark;
      if (history.length) {
        let check = history[0].bookmarks.includes(this.entry.id);
        if (this.keyInObj('user', this.entry)) {
          check = check || this.entry.user.bookmarked;
        }
        return check;
      }
      return false;
    },
    next() {
      this.$emit('next', this.entry);
      this.dialog = false;
    },
    previous() {
      this.$emit('previous', this.entry);
      this.dialog = false;
    },
  },
  computed: {
    update() {
      return this.entry;
    },
    title() {
      const title = [];
      this.entry.meta.forEach(({ name, value_str }) => {
        if (name === 'title' && value_str) {
          title.push(value_str);
        }
      });
      if (title.length) return title[0];
      return this.$t('griditem.notitle');
    },
    artist() {
      const artist = [];
      this.entry.meta.forEach(({ name, value_str }) => {
        if (name === 'artist_name' && value_str) {
          artist.push(value_str);
        }
      });
      if (artist.length) return artist.join(', ');
      return this.$t('griditem.noartist');
    },
    settings() {
      return this.$store.state.api.settings;
    },
    getCss() {
      return {
        height: this.height,
        width: this.width,
        cursor: 'pointer',
      };
    },
  },
  watch: {
    update() {
      this.bookmarked = this.isBookmarked();
    },
    settings: {
      handler() {
        this.updateSize();
      },
      deep: true,
    },
    showDialog(value) {
      this.dialog = value;
    },
  },
  created() {
    this.bookmarked = this.isBookmarked();
    this.updateSize();
  },
  components: {
    ModalItem,
  },
};
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
.grid-item:hover>.bookmark button {
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
</style>
