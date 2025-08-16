<template>
  <v-hover
    v-if="!isDisabled"
    v-slot="{ isHovering, props: activatorProps }"
  >
    <div
      v-bind="activatorProps"
      class="grid-item"
      :disabled="isDisabled ? true : undefined"
      @click="openDialog"
      @keydown.enter.prevent="openDialog"
      @keydown.space.prevent="openDialog"
    >
      <img
        :src="item.path"
        :alt="titles[0]"
        loading="lazy"
        decoding="async"
        @error="onError"
        @load="onLoad"
      >

      <v-fade-transition>
        <div
          v-if="isLoaded && isHovering"
          class="overlay"
        >
          <div class="overlay__content">
            <div
              class="overlay__title text-subtitle-1"
              :title="titles[0]"
            >
              <b>{{ titles[0] }}</b>
            </div>

            <div
              class="overlay__creators text-caption"
              :title="creatorsLabel"
            >
              {{ creatorsLabel }}
            </div>
          </div>
        </div>
      </v-fade-transition>
    </div>
  </v-hover>

  <ResourceDialog
    v-model="dialog"
    :item="item"
  />
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import useResource from '@/composables/useResource'
import ResourceDialog from '@/components/dialogs/ResourceDialog.vue'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

const {
  isLoaded,
  isDisabled,
  onLoad,
  onError,
  titles,
  creators
} = useResource(props.item)

const creatorsLabel = computed(() =>
  Array.isArray(creators?.value) ? creators.value.join(', ') : ''
)

const emit = defineEmits(['disabled'])
watch(isDisabled, (value) => {
  if (value) {
    emit('disabled', true)
  }
})

const dialog = ref(false)
function openDialog() {
  dialog.value = true
}
</script>

<style scoped>
.overlay {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  position: absolute;
  background: linear-gradient(to top, black, #0000 40%);
  transform: translate(-50%, -50%);
  object-fit: cover;
  min-width: 100%;
  max-width: 100%;
  color: #fff;
  height: 100%;
  left: 50%;
  top: 50%;
}

.overlay__content {
  padding: 16px;
}

.overlay__title,
.overlay__creators {
  text-overflow: ellipsis;
  line-height: 1.25rem;
  white-space: nowrap;
  overflow: hidden;
}
</style>