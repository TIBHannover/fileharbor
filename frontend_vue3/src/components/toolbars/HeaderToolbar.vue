<template>
  <v-app-bar
    class="border-b-sm"
    flat
  >
    <v-app-bar-nav-icon @click="$emit('toggle-drawer')" />
    
    <v-toolbar-title class="mr-5">
      <LogoTemplate />
    </v-toolbar-title>

    <SearchDialog modality="text">
      <template #activator>
        <v-btn
          class="ml-2"
          color="grey"
          variant="tonal"
        >
          {{ $t("search.dialog.modality.text") }}
        </v-btn>
      </template>
    </SearchDialog>

    <SearchDialog modality="images">
      <template #activator>
        <v-btn
          class="ml-2"
          color="grey"
          variant="tonal"
        >
          {{ $t("search.dialog.modality.images") }}
        </v-btn>
      </template>
    </SearchDialog>

    <v-spacer />

    <SearchDialog />
  </v-app-bar>
</template>

<script setup>
import LogoTemplate from '@/components/LogoTemplate.vue'
import SearchDialog from '@/components/dialogs/SearchDialog.vue'

defineEmits(['toggle-drawer'])
</script>

<style scoped>
.v-toolbar-title {
  flex: none;
}
</style>