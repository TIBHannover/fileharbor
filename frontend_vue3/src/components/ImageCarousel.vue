<template>
  <v-slide-group
    v-if="item.images.length > 1"
    class="image-overview"
    show-arrows="always"
    mandatory
  >
    <v-slide-group-item
      v-for="image in item.images"
      :key="image.path"
    >
      <v-img
        :src="image.path"
        class="bg-grey-lighten-2 mx-1"
        style="max-width: 125px"
        loading="lazy"
        decoding="async"
        width="125"
        height="85"
      />
    </v-slide-group-item>
  </v-slide-group>
</template>

<script setup>
const props = defineProps({
  item: {
    type: Object,
    required: true
  }
})
</script>

<style scoped>
.image-overview {
  width: 100%;
}
</style>