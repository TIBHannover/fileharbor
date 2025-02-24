<template>
  <v-card>
    <v-card-title class="mb-2">
      {{ $t("modal.collection.upload.title") }}

      <v-btn
        @click.native="close"
        absolute
        top
        right
        icon
      >
        <v-icon>mdi-close</v-icon>
      </v-btn>
    </v-card-title>

    <v-card-text>
      <v-form v-model="isFormValid">
        <v-text-field
          v-model="collection.name"
          :placeholder="$t('modal.collection.upload.name')"
          :rules="[checkLength]"
          tabindex="1"
          counter="25"
          clearable
        />

        <v-file-input
          v-model="collection.image"
          accept=".zip, .tar, .tar.gz, .tar.bz2, .tar.xz"
          :placeholder="$t('modal.collection.upload.imagefile.label')"
          prepend-icon="mdi-image-outline"
          :rules="[checkImageFile]"
          tabindex="2"
          show-size
        />

        <v-file-input
          v-model="collection.meta"
          accept=".csv, .json, .jsonl"
          :placeholder="$t('modal.collection.upload.metafile.label')"
          prepend-icon="mdi-text-box-outline"
          :error-messages="errorMessage"
          :rules="[checkMetaFile]"
          tabindex="3"
          show-size
        />
      </v-form>
    </v-card-text>

    <v-card-actions class="px-6 pb-6">
      <v-btn
        :disabled="!isFormValid"
        tabindex="4"
        @click="upload"
        color="accent"
        depressed
        rounded
        block
      >
        {{ $t("button.upload") }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
export default {
  props: {
    value: Boolean,
  },
  data() {
    return {
      collection: {},
      isFormValid: false,
    };
  },
  computed: {
    errorMessage() {
      if (this.keyInObj('status', this.upload) && this.upload.status === 'error') {
        const errorTypes = this.$t('modal.collection.upload.error');
        if (
          this.keyInObj('error', this.upload)
          && this.keyInObj(this.upload.error.type, errorTypes)
        ) {
          if (this.upload.error.type === 'unknown_fields') {
            return this.$t('modal.collection.upload.metafile.unknown', {
              field_names: this.upload.unknown_fields.join(', '),
            });
          }
          return errorTypes[this.upload.error.type];
        }
        return this.$t('modal.collection.upload.error.default');
      }
      return null;
    },
  },
  methods: {
    upload() {
      this.$store.dispatch('collection/upload', this.collection).then(() => {
        this.close();
        this.collection = {};
        const update = { modal: 'list', value: true };
        this.$store.commit('collection/updateModal', update);
      });
    },
    close() {
      this.$emit('input', false);
    },
    checkImageFile() {
      const value = this.collection.image;
      if (value) {
        if (value.size < 2000000000) {
          return true;
        }
        return this.$tc('modal.search.file.rule', 2000);
      }
      return this.$t('field.required');
    },
    checkMetaFile() {
      const value = this.collection.meta;
      if (value) {
        if (value.size < 20000000) {
          return true;
        }
        return this.$tc('modal.search.file.rule', 200);
      }
      return true;
    },
    checkLength(value) {
      if (value) {
        if (value.length < 5) {
          return this.$tc('user.register.rules.min', 5);
        }
        if (value.length > 25) {
          return this.$tc('user.register.rules.max', 25);
        }
        return true;
      }
      return this.$t('field.required');
    },
  },
};
</script>
