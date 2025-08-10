<template>
  <v-hover
    v-if="!isDisabled"
    v-slot="{ isHovering, props: activatorProps }"
  >
    <div
      v-bind="activatorProps"
      class="grid-item"
      :disabled="isDisabled ? true : undefined"
    >
      <img
        :src="item.path"
        alt=""
        @error="onError"
        @load="onLoad"
      >

      <v-fade-transition>
        <v-container
          v-if="isLoaded && isHovering"
          class="overlay"
        >
          Test
        </v-container>
      </v-fade-transition>
    </div>
  </v-hover>
</template>

<script setup>
import { watch } from 'vue'
import useResource from '@/composables/useResource'

const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})

const {
  isLoaded,
  isDisabled
} = useResource(props.item)

const emit = defineEmits(['disabled'])
watch(isDisabled, (value) => {
  if (value) {
    emit('disabled', true)
  }
})
</script>

<style scoped>
.v-container {
  position: absolute;
  flex-direction: column;
  display: flex;
  width: 100%;
  height: 100%;
  bottom: 0;
  left: 0;
}

.v-container .overlay {
  background: linear-gradient(to top, black, #0000 40%);
  transform: translate(-50%, -50%);
  position: absolute;
  object-fit: cover;
  min-width: 100%;
  max-width: 100%;
  color: #fff;
  height: 100%;
  left: 50%;
  top: 50%;
}
</style>