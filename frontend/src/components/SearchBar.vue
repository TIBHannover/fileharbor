<template>
  <div id="search-general">
    <v-combobox
      v-model="query"
      class="mx-1 sbar"
      ref="combobox"
      @click:clear="remove(-1)"
      @keyup.enter="submit($event, random=false)"
      :items="queryExamples"
      :placeholder="$t('home.search.placeholder')"
      allow-overflow
      rounded
      solo
      hide-details
      flat
      clearable
      multiple
      single-line
      outlined
    >
      <template v-slot:prepend-inner>
        <v-btn
          :title="$t('button.search')"
          @click.stop="submit"
          small
          icon
        >
          <v-icon>
            mdi-magnify
          </v-icon>
        </v-btn>

        <v-btn
          id="search-random"
          :title="$t('search.random')"
          class="ml-1"
          @click.stop="submit($event, random=true)"
          small
          icon
        >
          <v-icon>
            mdi-slot-machine-outline
          </v-icon>
        </v-btn>
      </template>

      <template v-slot:append>
        <v-select
          v-model="lang"
          :items="langItems"
          :title="$t('home.search.lang')"
          @change="updateLang"
          class="lang"
          single-line
          hide-details
          solo
          flat
        />

        <ModalSearch @clicked="hideMenu" />
      </template>

      <template v-slot:item="{ attrs, item }">
        <v-chip
          v-for="entry in item.entries"
          :key="entry.value"
          v-bind="attrs"
          class="mr-2"
        >
          <v-btn
            v-if="entry.positive"
            class="ml-n2"
            icon
            small
          >
            <v-icon>mdi-plus</v-icon>
          </v-btn>
          <v-btn
            v-else
            class="ml-n2"
            icon
            small
          >
            <v-icon>mdi-minus</v-icon>
          </v-btn>

          <v-icon
            v-if="entry.type === 'idx'"
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
            v-if="entry.type === 'idx'"
            :title="entry.label"
          >
            {{ entry.label }}
          </span>
          <span
            v-else
            :title="entry.value"
          >
            {{ entry.value }}
          </span>
        </v-chip>
      </template>

      <template v-slot:selection="{ attrs, selected, item, index }">
        <v-menu
          :close-on-content-click="false"
          min-width="300"
          max-width="300"
          offset-y
          bottom
          right
          open-on-hover
        >
          <template v-slot:activator="{ on }">
            <v-chip
              v-on="on"
              v-bind="attrs"
              :input-value="selected"
              @click:close="remove(index)"
              close
            >
              <v-btn
                v-if="item.positive"
                @click="toggle(index)"
                :title="$t('home.search.query.negative')"
                class="ml-n2"
                icon
                small
              >
                <v-icon>mdi-plus</v-icon>
              </v-btn>
              <v-btn
                v-else
                @click="toggle(index)"
                :title="$t('home.search.query.positive')"
                class="ml-n2"
                icon
                small
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

          <div
            v-if="item.type === 'idx' && item.preview"
            style="margin-left:auto; margin-right:auto; height:100%"
          >
            <ROISelector
              v-model="item.roi"
              :key="item.value"
              :src="item.preview"
              class="grey lighten-1"
              @update="updateROI(index, ...arguments)"
              max-height="200px"
              contain
            />
          </div>

          <div v-if="item.type === 'idx'">
            <Weights
              v-model="item.weights"
              :key="item.value"
              :local="true"
              @update="updateWeights(index, ...arguments)"
            />

            <div class="pa-6">
              <v-btn
                @click="submitQueryStore"
                color="accent"
                block
                rounded
                depressed
              >
                {{ $t("button.update") }}
              </v-btn>
            </div>
          </div>
        </v-menu>
      </template>
    </v-combobox>
  </div>
</template>

<script>
import Weights from '@/components/Weights.vue';
import ModalSearch from '@/components/ModalSearch.vue';
import ROISelector from '@/components/ROISelector.vue';

export default {
  data() {
    return {
      lang: this.$store.state.api.lang.toUpperCase(),
      langItems: ['EN'],
      queryExamples: [
        { header: this.$t('home.search.examples') },
        {
          example: true,
          entries: [
            { type: 'idx', positive: true, value: '3fa6b53c7e163ebd9663a01ab3efd24a', label: 'Salvator Mundi' },
          ],
        },
        {
          example: true,
          entries: [
            { type: 'txt', positive: true, value: 'adam and eve' },
            { type: 'txt', positive: false, value: 'hercules' },
          ],
        },
        {
          example: true,
          entries: [
            { type: 'txt', positive: true, value: 'too much alcohol' },
          ],
        },
        {
          example: true,
          entries: [
            { type: 'txt', positive: true, value: 'ceiling painting' },
            { type: 'txt', positive: true, value: 'cabinet' },
          ],
        },
      ],
      query: this.$store.state.api.query,
      queryStore: [],
    };
  },
  methods: {
    hideMenu() {
      this.$refs.combobox.isMenuActive = false;
      document.activeElement.blur();
    },
    submit(event, random = false) {
      this.$store.commit('api/updateRandom', random);
      this.$store.dispatch('api/load');
      this.hideMenu();
    },
    submitQueryStore() {
      this.queryStore.forEach(({ index, value, type }) => {
        if (type === 'weights') {
          this.query[index].weights = value;
        } else if (type === 'roi') {
          this.query[index].roi = value;
        }
      });
      this.queryStore = [];
    },
    remove(index) {
      if (index === -1) {
        this.query = [];
      } else {
        this.query.splice(index, 1);
      }
    },
    toggle(index) {
      const { positive } = this.query[index];
      this.query[index].positive = !positive;
    },
    updateLang(value) {
      this.$store.commit('api/updateLang', value.toLowerCase());
    },
    updateWeights(index, value) {
      this.queryStore.push({ index, value, type: 'weights' });
    },
    updateROI(index, value) {
      this.queryStore.push({ index, value, type: 'roi' });
    },
  },
  computed: {
    updateQuery() {
      return this.$store.state.api.query;
    },
  },
  watch: {
    query: {
      handler(newValues, oldValues) {
        if (!this.isEqual(newValues, oldValues)) {
          let query = [];
          newValues.every((value) => {
            if (typeof value === 'string') {
              let positive = true;
              if (value.charAt(0) === '-') {
                value = value.slice(1);
                positive = false;
              }
              query.push({ type: 'txt', positive, value });
            } else if (typeof value === 'object') {
              if (value.example) {
                query = value.entries;
                return false;
              }
              query.push(value);
            }
            return true;
          });
          this.$store.commit('api/updateQuery', query);
        }
      },
      deep: true,
    },
    updateQuery: {
      handler(values) {
        this.query = values;
        if (!this.$store.state.api.random && values.length) {
          this.submit();
        }
      },
      deep: true,
    },
  },
  components: {
    Weights,
    ModalSearch,
    ROISelector,
  },
};
</script>

<style>
.v-chip .v-avatar {
  padding-top: 3px;
}

.v-input .v-btn {
  letter-spacing: 1;
}

.v-application--is-ltr .v-text-field.v-text-field .v-input__prepend-inner {
  padding-right: 12px;
}

.v-select.v-select--is-menu-active .v-input__icon--append .v-icon {
  transform: rotate(0deg);
}

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

header .v-autocomplete .v-text-field.v-text-field--solo .v-input__control input {
  max-width: fit-content;
  min-width: 0;
}

.sbar.v-autocomplete .v-select__selections {
  -ms-overflow-style: none;
  scrollbar-width: none;
  flex-wrap: nowrap;
  overflow-x: auto;
  overflow-y: hidden;
}

.sbar.v-autocomplete .v-select__selections::-webkit-scrollbar {
  height: 0;
  width: 0;
}

.sbar.v-autocomplete .v-select__selections>.v-chip {
  overflow: initial;
}

.theme--light.v-icon,
.v-dialog .v-expansion-panel-content__wrap .capitalize {
  color: rgba(69, 123, 157, 0.54);
}

.v-input__icon--append .theme--light.v-icon:not(.mdi-menu-down),
.v-input__prepend-inner .theme--light.v-icon {
  color: rgba(0, 0, 0, 0.54);
}

.v-main .theme--light.v-text-field--outlined:not(.v-input--is-focused):not(.v-input--has-state) > .v-input__control > .v-input__slot fieldset {
  border: 3px solid;
  color: #f5f5f5;
}

.v-main .v-text-field--outlined.v-input--has-state fieldset,
.v-main .v-text-field--outlined.v-input--is-focused fieldset {
  border: 3px solid;
}

header .theme--light.v-text-field--outlined:not(.v-input--is-focused):not(.v-input--has-state) > .v-input__control > .v-input__slot fieldset {
  border: 0px solid;
}

header .v-text-field--outlined.v-input--has-state fieldset,
header .v-text-field--outlined.v-input--is-focused fieldset {
  border: 0px solid;
}

header .v-text-field--filled > .v-input__control > .v-input__slot,
header .v-text-field--full-width > .v-input__control > .v-input__slot,
header .v-text-field--outlined > .v-input__control > .v-input__slot {
  min-height: 48px;
}

.v-chip__content .v-btn__content {
  justify-content: center;
}

.v-input.lang {
  font-family: "Roboto Mono", monospace;
  text-transform: uppercase;
  width: min-content;
}

.v-input.lang > .v-input__control > .v-input__slot {
  padding: 0 6px !important;
}

.v-input.lang > .v-input__control .v-select__selections > input {
  display: none;
}

.v-input.lang .v-input__append-inner {
  display: none;
}
</style>
