<template>
  <div class="cluster-view mb-n6">
    <div
      v-for="(entries, cluster) in convertedEntries"
      :key="entries[0].id"
      class="mt-4 mb-6"
    >
      <div class="text-h6 mx-3 mb-4">
        {{ $t("field.cluster") }} {{ parseInt(cluster) + 1 }}

        <span class="v-label theme--light ml-1 mr-4">
           · {{ entries.length }}

          <span v-if="entries.length===1">
            {{ $t("field.object") }}
          </span>
          <span v-else>
            {{ $t("field.objects") }}
          </span>
        </span>

        <v-chip
          v-for="(tag, cluster) in clusterTags[cluster]"
          :key="cluster"
          class="ml-1"
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
        </v-chip>
      </div>

      <v-slide-group
        v-model="slide[cluster]"
        @click:next="next(cluster)"
        @click:prev="prev(cluster)"
        show-arrows
      >
        <v-slide-item
          v-for="(entry, index) in reducedEntries[cluster]"
          :key="entry.id"
        >
          <GridItem
            :entry="entry"
            :isFirst="index === 0"
            :isLast="index === reducedEntries[cluster].length - 1"
            :showDialog="currentDialog === entry.id"
            @next="nextEntry(cluster, ...arguments)"
            @previous="previousEntry(cluster, ...arguments)"
          />
        </v-slide-item>

        <div
          v-if="reducedEntries[cluster].length < 4"
          class="grid-item-fill"
        >
        </div>
      </v-slide-group>
    </div>
  </div>
</template>

<script>
import Vue from 'vue';
import { EXCLUDE_ANNOTATION_NAMES, PLUGIN_ICONS } from '@/../app.config';
import GridItem from '@/components/GridItem.vue';

export default {
  props: ['entries'],
  data() {
    return {
      slide: {},
      clusterTags: {},
      reducedEntries: {},
      currentDialog: null,
      pluginIcons: PLUGIN_ICONS,
    };
  },
  methods: {
    next(index) {
      this.slide[index] += 5;
      this.reduceEntries(index);
    },
    prev(index) {
      this.slide[index] -= 5;
      this.reduceEntries(index);
    },
    nextEntry(cluster, entry) {
      const entries = this.reducedEntries[cluster];
      const index = entries.indexOf(entry);
      if (index + 1 < entries.length) {
        const entry = entries[index + 1];
        this.currentDialog = entry.id;
      }
    },
    previousEntry(cluster, entry) {
      const entries = this.reducedEntries[cluster];
      const index = entries.indexOf(entry);
      if (index > 0) {
        const entry = entries[index - 1];
        this.currentDialog = entry.id;
      }
    },
    reduceEntries(cluster) {
      const nEntries = 25 + this.slide[cluster];
      let values = this.convertedEntries[cluster];
      if (values.length > nEntries) {
        values = values.slice(0, nEntries);
        this.reducedEntries[cluster] = values;
      }
    },
  },
  computed: {
    convertedEntries() {
      const entries = {};
      this.entries.forEach((entry) => {
        if (entries[entry.cluster] instanceof Array) {
          entries[entry.cluster].push(entry);
        } else {
          entries[entry.cluster] = [entry];
        }
      });
      return entries;
    },
  },
  watch: {
    convertedEntries: {
      handler(entries) {
        this.slide = {};
        this.clusterTags = {};
        this.reducedEntries = {};
        Object.keys(entries).forEach((cluster) => {
          let tags = [];
          const pluginTags = {};
          const values = entries[cluster].slice(0, 25);
          values.forEach(({ classifier }) => {
            classifier.forEach(({ plugin, annotations }) => {
              if (!this.keyInObj(plugin, pluginTags)) {
                pluginTags[plugin] = {};
              }
              annotations.forEach(({ name, value }) => {
                if (!EXCLUDE_ANNOTATION_NAMES.includes(name) && value >= 0.1) {
                  if (this.keyInObj(name, pluginTags[plugin])) {
                    pluginTags[plugin][name] += 1;
                  } else {
                    pluginTags[plugin][name] = 1;
                  }
                }
              });
            });
          });
          Object.keys(pluginTags).forEach((plugin) => {
            Object.keys(pluginTags[plugin]).forEach((name) => {
              const count = pluginTags[plugin][name];
              if (count > 9) {
                tags.push({ plugin, name, count });
              }
            });
          });
          tags.sort((a, b) => b.count - a.count);
          tags = tags.slice(0, 4);
          Vue.set(this.slide, cluster, 0);
          Vue.set(this.clusterTags, cluster, tags);
          Vue.set(this.reducedEntries, cluster, values);
        });
      },
      immediate: true,
    },
  },
  components: {
    GridItem,
  },
};
</script>

<style>
.cluster-view .text-h6 {
  font-size: 1.15rem !important;
  align-items: center;
  display: flex;
}

.cluster-view .text-h6 > .v-label {
  font-size: 14px;
  cursor: auto;
}

.cluster-view .v-slide-group__next,
.cluster-view .v-slide-group__prev {
  flex: 0 1 36px;
  min-width: 36px;
}

.cluster-view .v-slide-group:not(.v-slide-group--has-affixes) > .v-slide-group__next,
.cluster-view .v-slide-group:not(.v-slide-group--has-affixes) > .v-slide-group__prev {
  display: flex;
}

.cluster-view .v-slide-group__next--disabled > .theme--light.v-icon.v-icon.v-icon--disabled,
.cluster-view .v-slide-group__prev--disabled > .theme--light.v-icon.v-icon.v-icon--disabled {
  color: rgba(69, 123, 157, .2) !important;
}

.cluster-view span.clip {
  text-overflow: ellipsis;
  overflow: hidden;
  max-width: 155px;
}
</style>
