<template>
  <v-bottom-navigation>
    <v-btn
      @click="imprint"
      text
    >
      {{ $t("imprint.title") }}
    </v-btn>

    <v-btn
      @click="privacy"
      text
    >
      {{ $t("privacy.title") }}
    </v-btn>
  </v-bottom-navigation>
</template>

<script>
import router from '@/router';

export default {
  methods: {
    imprint() {
      router.push({ path: 'imprint' });
    },
    privacy() {
      router.push({ path: 'privacy' });
    },
  },
};
</script>

<style scoped>
.v-bottom-navigation {
  box-shadow: none !important;
}
</style>
