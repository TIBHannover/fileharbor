<template>
  <SearchDialog
    v-if="params.modality === 'text'"
    modality="text"
  >
    <template #activator>
      <v-text-field
        :placeholder="params.query"
        variant="outlined"
        density="compact"
        hide-details
        clearable
        rounded
        inset
      >
        <template #prepend-inner>
          <v-icon>
            mdi-format-text
          </v-icon>
        </template>

        <template #append-inner>
          <v-badge
            color="error"
            :content="params.dataset.length"
            :max-height="18"
            inline
          >
            <v-icon
              icon="mdi-database"
              size="small"
            />
          </v-badge>
        </template>

        <template #append>
          <v-btn
            icon="mdi-magnify"
            density="compact"
            variant="flat"
          />
        </template>
      </v-text-field>
    </template>
  </SearchDialog>

  <SearchDialog
    v-if="params.modality === 'images'"
    modality="images"
  >
    <template #activator>
      <v-text-field
        :placeholder="params.query"
        variant="outlined"
        density="compact"
        hide-details
        clearable
        rounded
        inset
      >
        <template #prepend-inner>
          <v-icon>
            mdi-image-outline
          </v-icon>
        </template>

        <template #append-inner>
          <v-badge
            color="error"
            :content="params.similarity.length"
            :max-height="18"
            inline
          >
            <v-icon
              icon="mdi-vector-intersection"
              size="small"
            />
          </v-badge>

          <v-badge
            color="error"
            :content="params.dataset.length"
            :max-height="18"
            inline
          >
            <v-icon
              icon="mdi-database"
              size="small"
            />
          </v-badge>
        </template>

        <template #append>
          <v-btn
            icon="mdi-magnify"
            density="compact"
            variant="flat"
          />
        </template>
      </v-text-field>
    </template>
  </SearchDialog>
</template>

<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useSearchStore } from '@/stores/search'
import SearchDialog from '@/components/dialogs/SearchDialog.vue'

const search = useSearchStore()
const { params } = storeToRefs(search)
</script>