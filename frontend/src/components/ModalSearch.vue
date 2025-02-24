<template>
  <v-dialog v-model="dialog" max-width="350px">
    <template v-slot:activator="{ on }">
      <v-btn
        id="search-image"
        v-on="on"
        @click="clicked"
        :title="$t('modal.search.title')"
        class="my-auto"
        small
        icon
      >
        <v-icon> mdi-image-outline </v-icon>
      </v-btn>
    </template>

    <v-card>
      <v-card-title>
        <div class="text-h6">
          {{ $t("modal.search.title") }}
        </div>

        <v-btn @click.native="dialog = false" absolute right icon top>
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text>
        <v-form v-model="isFormValid">
          <v-switch
            v-model="selectFile"
            class="pt-1 pb-2"
            :label="$t('modal.search.toggle')"
            color="secondary"
            hide-details
            inset
          />

          <v-file-input
            v-if="selectFile"
            v-model="user.file"
            accept="image/png, image/jpeg, image/gif"
            :placeholder="$t('modal.search.file.label')"
            prepend-icon="mdi-camera"
            :rules="checkFile"
            tabindex="1"
            show-size
          />

          <v-text-field
            v-else
            v-model="user.url"
            :placeholder="$t('modal.search.url.label')"
            prepend-icon="mdi-link-variant"
            :rules="checkURL"
            tabindex="1"
            clearable
          />
        </v-form>
      </v-card-text>

      <v-card-actions class="px-6 pb-6">
        <v-menu offset-y bottom right>
          <template v-slot:activator="{ attrs, on: menu }">
            <v-btn
              v-bind="attrs"
              v-on="menu"
              :disabled="!isFormValid"
              color="accent"
              tabindex="2"
              depressed
              rounded
              block
            >
              {{ $t("button.submit") }}
            </v-btn>
          </template>

          <v-list class="pa-0">
            <v-list-item @click="search(false)">
              {{ $t("search.new") }}
            </v-list-item>

            <v-list-item @click="search(true)">
              {{ $t("search.append") }}
            </v-list-item>
          </v-list>
        </v-menu>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import isURL from "validator/lib/isURL";
import router from "@/router";

export default {
  data() {
    return {
      user: {
        url: null,
        file: null,
      },
      dialog: false,
      selectFile: false,
      isFormValid: false,
    };
  },
  methods: {
    clicked() {
      this.$emit("clicked");
    },
    search(append) {
      const query = { positive: true, append };
      if (this.selectFile) {
        query.type = "file";
        query.value = this.user.file;
      } else {
        query.type = "url";
        query.value = this.user.url;
      }
      this.$store.dispatch("api/upload", query).then(() => {
        this.user = { url: null, file: null };
        this.dialog = false;
        if (router.currentRoute.path !== "/search") {
          router.push("/search");
        }
      });
    },
  },
  computed: {
    checkURL() {
      if (!this.selectFile) {
        return [
          (v) => !!v || this.$t("field.required"),
          (v) =>
            (v && v.length && isURL(v)) || this.$t("modal.search.url.rule"),
        ];
      }
      return true;
    },
    checkFile() {
      if (this.selectFile) {
        const fileSize = 20; // in MB
        return [
          (v) => !!v || this.$t("field.required"),
          (v) =>
            (v && v.size < fileSize * 1000000) ||
            this.$tc("modal.search.file.rule", fileSize),
        ];
      }
      return true;
    },
  },
};
</script>

<style>
.v-text-field__details,
.v-text-field__details > div {
  min-height: 0;
}
</style>
