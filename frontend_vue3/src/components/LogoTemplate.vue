<template>
  <button
    class="d-flex"
    @click="goTo('home')"
    @keydown.enter="goTo('home')"
  >
    <img
      alt="iART"
      src="/logo.svg"
      height="32"
    >
  </button>
</template>

<script setup>
import goTo from '@/composables/useGoTo'
</script>