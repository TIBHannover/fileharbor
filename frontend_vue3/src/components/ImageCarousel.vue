<template>
  <v-slide-group
    class="image-overview"
    show-arrows="always"
    mandatory
  >
    <v-slide-group-item
      v-for="n in 3"
      :key="n"
    >
      <v-img
        :src="item.path"
        class="bg-grey-lighten-2 mx-1"
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