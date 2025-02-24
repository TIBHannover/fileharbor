<template>
  <v-dialog
    :value="value"
    @input="$emit('input')"
    @keydown.left="getPrevious"
    @keydown.right="getNext"
    max-width="750px"
  >
    <v-btn
      class="middle"
      @click="getPrevious"
      :disabled="isFirst"
      absolute
      x-large
      icon
      left
      top
    >
      <v-icon
        color="white"
        size="56"
      >
        mdi-chevron-left
      </v-icon>
    </v-btn>

    <v-btn
      class="middle"
      @click="getNext"
      :disabled="isLast"
      icon
      absolute
      top
      right
      x-large
    >
      <v-icon
        color="white"
        size="56"
      >
        mdi-chevron-right
      </v-icon>
    </v-btn>

    <v-card>
      <div class="img-wrapper">
        <div style="margin-left:auto; margin-right:auto; height:100%">
          <ROISelector
            v-model="roi"
            :lazy-src="entry.preview"
            :src="entry.path"
            @update="updateROI"
            class="grey lighten-1"
            max-height="500px"
            contain
          >
            <template v-slot:placeholder>
              <v-row
                class="fill-height ma-0"
                align="center"
                justify="center"
              >
                <v-progress-circular indeterminate />
              </v-row>
            </template>

            <template v-slot:context>
              <v-list class="pa-0">
                <v-list-item @click="query(null, false, 'idx')">
                  {{ $t('search.new') }}
                </v-list-item>

                <v-list-item @click="query(null, true, 'idx')">
                  {{ $t('search.append') }}
                </v-list-item>
              </v-list>
            </template>
          </ROISelector>
        </div>

        <v-btn
          @click.native="$emit('input')"
          icon
          absolute
          top
          right
        >
          <v-icon>mdi-close</v-icon>
        </v-btn>

        <v-menu
          offset-y
          bottom
          right
        >
          <template v-slot:activator="{ attrs, on: menu }">
            <v-fab-transition>
              <v-btn
                v-bind="attrs"
                v-on="menu"
                :title="$t('search.object')"
                color="accent"
                depressed
                absolute
                bottom
                right
                large
                fab
              >
                <v-icon color="white">mdi-magnify</v-icon>
              </v-btn>
            </v-fab-transition>
          </template>

          <v-list class="pa-0">
            <v-list-item @click="query(null, false, 'idx')">
              {{ $t('search.new') }}
            </v-list-item>

            <v-list-item @click="query(null, true, 'idx')">
              {{ $t('search.append') }}
            </v-list-item>
          </v-list>
        </v-menu>
      </div>

      <v-card-title class="mb-2">
        <div class="text-h5 max-w mr-16">
          <span
            v-for="(name, index) in title"
            :key="index"
            @click="query(name, true, 'txt')"
          >
            {{ name }}
          </span>

          <v-chip
            v-if="date"
            class="ml-3"
          >
            <v-icon
              color="grey darken-1"
              left
            >
              mdi-clock-time-four-outline
            </v-icon>

            <span>{{ date }}</span>
          </v-chip>
        </div>

        <div class="artist text-h6 max-w font-weight-regular grey--text mt-1">
          <span
            v-for="(name, index) in artist"
            :key="index"
            @click="filter(name, 'meta.artist_name')"
          >
            {{ name }}
          </span>
        </div>
      </v-card-title>

      <v-card-text>
        <div
          v-if="keywords.length"
          class="mb-2"
        >
          <v-chip
            v-for="(tag, index) in keywords"
            :key="index"
            class="mr-1 mb-2"
            :text-color="tag.disable ? 'grey lighten-1' : ''"
            outlined
          >
            <span
              class="tag clip"
              :title="tag.name"
            >
              {{ tag.name }}
            </span>

            <v-icon
              class="ml-1"
              size="18"
              :title="$t('plugin')[tag.plugin]"
            >
              {{ pluginIcons[tag.plugin] }}
            </v-icon>

            <v-icon
              v-if="tag.disable"
              class="ml-1 mr-n1"
              size="14"
            >
              mdi-help
            </v-icon>
          </v-chip>

          <v-btn
            v-if="moreTags"
            @click="moreTags=false"
            :title="$t('modal.item.tags.more')"
            class="mb-2"
            color="grey lighten-2"
            icon
            small
            depressed
          >
            <v-icon>mdi-tag-plus</v-icon>
          </v-btn>

          <v-btn
            v-else
            @click="moreTags=true"
            :title="$t('modal.item.tags.less')"
            class="mb-2"
            color="grey lighten-2"
            icon
            small
            depressed
          >
            <v-icon>mdi-tag-minus</v-icon>
          </v-btn>
        </div>

        <v-expansion-panels
          accordion
          multiple
          flat
        >
          <v-expansion-panel v-if="Object.keys(metadata).length">
            <v-expansion-panel-header class="pa-0">
              <v-icon
                class="mr-3"
                size="18"
              >
                mdi-information-outline
              </v-icon>

              <span class="text-subtitle-1">
                {{ $t('modal.item.information') }}
              </span>
            </v-expansion-panel-header>

            <v-expansion-panel-content>
              <v-row
                v-for="(values, field, index) in metadata"
                :key="index"
                justify="space-around"
                no-gutters
              >
                <v-col cols="3">
                  <span class="capitalize">
                    {{ $t('drawer.filter.field')[field] }}
                  </span>
                </v-col>

                <v-col cols="9">
                  <v-chip
                    v-for="(value, index) in values"
                    :key="index"
                    :disabled="value.disable"
                    class="mr-1 mb-2"
                    @click="filter(value.name, field)"
                    :title="$t('drawer.filter.title')"
                    outlined
                    :class="field.replace('.', '-')"
                  >
                    <span>{{ value.name }}</span>
                  </v-chip>
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>

          <v-expansion-panel v-if="texts.length">
            <v-expansion-panel-header class="pa-0">
              <v-icon
                class="mr-3"
                size="18"
              >
                mdi-tag-text-outline
              </v-icon>

              <span class="text-subtitle-1">
                {{ $t('modal.item.iconclass.text') }}
              </span>
            </v-expansion-panel-header>

            <v-expansion-panel-content>
              <v-row
                justify="space-around"
                no-gutters
              >
                <v-col cols="3">
                  <span class="capitalize">
                    {{ $t('modal.item.iconclass.notations') }}
                  </span>
                </v-col>

                <v-col cols="9">
                  <v-chip
                    v-for="(tag, index) in texts"
                    :key="index"
                    :text-color="tag.disable ? 'grey lighten-1' : ''"
                    class="mr-1 mb-2"
                    outlined
                  >
                    <span
                      :title="tag.code+' '+tag.label"
                      class="clip"
                    >
                      {{ tag.code }} {{ tag.label }}
                    </span>

                    <v-icon
                      class="ml-1"
                      size="18"
                      :title="$t('plugin')[tag.plugin]"
                    >
                      {{ pluginIcons[tag.plugin] }}
                    </v-icon>

                    <v-icon
                      v-if="tag.disable"
                      class="ml-1 mr-n1"
                      size="14"
                    >
                      mdi-help
                    </v-icon>
                  </v-chip>
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>

          <v-expansion-panel v-if="references.length">
            <v-expansion-panel-header class="pa-0">
              <v-icon
                class="mr-3"
                size="18"
              >
                mdi-link-variant
              </v-icon>

              <span class="text-subtitle-1">{{ $t('modal.item.references') }}</span>
            </v-expansion-panel-header>

            <v-expansion-panel-content>
              <v-row
                v-for="(field, index) in references"
                :key="index"
                justify="space-around"
                no-gutters
              >
                <v-col cols="3">
                  <span class="capitalize">{{ field.name }}</span>
                </v-col>

                <v-col cols="9">
                  <v-chip
                    class="mr-1 mb-2"
                    :href="field.url"
                    target="_blank"
                    outlined
                  >
                    <span>{{ field.value }}</span>
                  </v-chip>
                </v-col>
              </v-row>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import { EXCLUDE_ANNOTATION_NAMES, PLUGIN_ICONS } from '../../app.config';
import ROISelector from '@/components/ROISelector.vue';

const scheme = new RegExp(
  /^(\d{1,2})([A-IK-Z]{1,2})?(\d+)?(\([^+)]+\))?(\d+)?(\(\+[0-9]+\))?$/,
  'm',
);
export default {
  props: {
    value: Boolean,
    entry: Object,
    isFirst: Boolean,
    isLast: Boolean,
  },
  data() {
    return {
      pluginIcons: PLUGIN_ICONS,
      moreTags: true,
      roi: null,
    };
  },
  methods: {
    query(value, append, type) {
      const query = { type, positive: true, value };
      if (type === 'idx') {
        query.value = this.entry.id;
        query.weights = {};
        query.roi = this.roi;
        query.label = this.title.join(' ');
        query.preview = this.entry.preview;
      }
      if (append) {
        this.$store.commit('api/addQuery', query);
      } else {
        this.$store.commit('api/updateQuery', [query]);
        this.$store.commit('api/removeAllFilters');
      }
      this.$store.commit('api/updateRandom', false);
      this.$emit('input');
    },
    filter(value, field) {
      const filter = { positive: true, name: value };
      this.$store.commit('api/addFilter', { field, filter });
      this.$emit('input');
    },
    updateROI(value) {
      this.roi = value;
    },
    getNext() {
      this.$emit('next');
    },
    getPrevious() {
      this.$emit('previous');
    },
  },
  computed: {
    title() {
      const title = [];
      this.entry.meta.forEach(({ name, value_str }) => {
        if (name === 'title' && value_str) {
          title.push(value_str);
        }
      });
      if (title.length) return title[0].split(' ');
      return [this.$t('griditem.notitle')];
    },
    artist() {
      const artist = [];
      this.entry.meta.forEach(({ name, value_str }) => {
        if (name === 'artist_name' && value_str) {
          artist.push(value_str);
        }
      });
      if (artist.length) return artist;
      return [this.$t('griditem.noartist')];
    },
    date() {
      let year_min = null;
      let year_max = null;
      this.entry.meta.forEach(({ name, value_str }) => {
        if (value_str) {
          if (name === 'year_min') {
            year_min = value_str;
          } else if (name === 'yaer_max') {
            year_max = value_str;
          }
        }
      });
      if (year_min && year_max) {
        if (year_min === year_max) {
          return year_min;
        }
        return `${year_min}–${year_max}`;
      }
      if (year_min) return year_min;
      if (year_max) return year_max;
      return null;
    },
    keywords() {
      const deselectedPlugins = [
        'iconclass_clip_classifier',
        'iconclass_lstm_classifier',
      ];
      let keywords = [];
      this.entry.classifier.forEach(({ plugin, annotations }) => {
        if (!deselectedPlugins.includes(plugin)) {
          annotations.forEach(({ name, value }) => {
            if (!EXCLUDE_ANNOTATION_NAMES.includes(name)) {
              keywords.push({
                name: name.split(',')[0],
                value,
                plugin,
                disable: value < 0.4,
              });
            }
          });
        }
      });
      keywords.sort((a, b) => b.value - a.value);
      if (this.moreTags && keywords.length >= 7) {
        keywords = keywords.slice(0, 7);
      }
      return keywords;
    },
    texts() {
      const selectedPlugins = [
        'iconclass_clip_classifier',
        'iconclass_lstm_classifier',
      ];
      const texts = [];
      this.entry.classifier.forEach(({ plugin, annotations }) => {
        if (selectedPlugins.includes(plugin)) {
          annotations.forEach(({ name, value }) => {
            if (!EXCLUDE_ANNOTATION_NAMES.includes(name)) {
              const [code, , label] = name.split('; ');
              const codeParts = scheme.exec(code).slice(1, 7);
              if (!codeParts[3]) {
                texts.push({
                  code,
                  label,
                  value,
                  plugin,
                  disable: value < 0.1,
                });
              }
            }
          });
        }
      });
      texts.sort((a, b) => b.value - a.value);
      return texts;
    },
    metadata() {
      const selectedFields = [
        'meta.depicts',
        'meta.genre',
        'meta.location',
        'meta.medium',
        'meta.object_type',
        'meta.institution',
      ];
      const meta = {};
      this.entry.meta.forEach(({ name, value_str }) => {
        const field = `meta.${name}`;
        if (selectedFields.includes(field)) {
          if (Object.prototype.hasOwnProperty.call(meta, field)) {
            meta[field].push({ name: value_str, disable: false });
          } else {
            meta[field] = [{ name: value_str, disable: false }];
          }
        }
      });
      const { id, name, user } = this.entry.collection;
      if (user) {
        meta.collection = [{ hash_id: id, name }];
      } else {
        this.entry.origin.forEach(({ name, value_str }) => {
          if (name === 'name') {
            meta['origin.name'] = [{ name: value_str, disable: false }];
          }
        });
      }
      return meta;
    },
    references() {
      const wd = 'https://www.wikidata.org/wiki/';
      const references = [];
      this.entry.meta.forEach(({ name, value_str }) => {
        if (name === 'wikidata' && value_str) {
          references.push({
            name,
            value: value_str,
            url: wd + value_str,
          });
        }
      });
      return references;
    },
  },
  components: {
    ROISelector,
  },
};
</script>

<style scoped>
.v-dialog .max-w {
  width: 100%;
}

.v-dialog .img-wrapper {
  position: relative;
}

.v-dialog .v-expansion-panel-header > :not(.v-expansion-panel-header__icon) {
  flex: initial;
}

.v-dialog .v-expansion-panel-content__wrap {
  padding: 0;
}

.v-dialog .text-h5,
.v-dialog .text-h6 {
  word-break: break-word;
}

.v-dialog .text-h5 > span,
.v-dialog .text-h6 > span,
.v-dialog .v-expansion-panel .capitalize,
.v-dialog .v-chip.origin-name,
.v-dialog .v-chip.collection {
  text-transform: capitalize;
}

.v-dialog .text-h6 > span,
.v-dialog .text-h5 > span {
  cursor: pointer;
}

.v-dialog .text-h6 > span:after {
  content: ", ";
}

.v-dialog .text-h6 > span:last-child:after {
  content: "";
}

.v-dialog .text-h5 > span:after {
  content: " ";
}

.v-dialog .text-h5 > span:last-child:after {
  content: "";
}

.v-dialog span.clip {
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 170px;
}

.v-dialog span.tag {
  text-transform: lowercase;
}

.v-dialog .v-btn.middle {
  margin-top: 50vh;
}
</style>
