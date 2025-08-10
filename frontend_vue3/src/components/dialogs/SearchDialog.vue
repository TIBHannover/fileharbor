<template>
  <v-dialog
    v-model="dialog"
    fullscreen
    transition="dialog-top-transition"
  >
    <template #activator="{ props: activatorProps }">
      <template v-if="$slots.activator">
        <span
          class="inline-flex"
          v-bind="activatorProps"
        >
          <slot name="activator" />
        </span>
      </template>
      <template v-else>
        <v-btn
          icon="mdi-magnify"
          v-bind="activatorProps"
        />
      </template>
    </template>

    <v-toolbar
      color="accent"
      flat
    >
      <template #append>
        <v-btn
          icon="mdi-close"
          @click="dialog = false"
        />
      </template>
    </v-toolbar>

    <v-card elevation="0">
      <v-container>
        <v-expansion-panels
          variant="accordion"
          multiple
          flat
        >
          <v-expansion-panel static>
            <v-expansion-panel-title>
              Test
            </v-expansion-panel-title>

            <v-expansion-panel-text>
              Test
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>

        <v-btn
          class="mt-4"
          color="grey"
          variant="outlined"
          block
          @click="onApply"
        >
          {{ $t('search.dialog.apply') }}
        </v-btn>
      </v-container>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { shallowRef } from 'vue'

const dialog = shallowRef(false)

// TODO: add params
const onApply = () => {
  search.post()
}
</script>

<style scoped>
.v-dialog {
  margin-bottom: 100px;
}
</style>