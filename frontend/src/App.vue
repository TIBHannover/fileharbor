<template>
  <div id="app">
    <ModalError />
    <router-view />
  </div>
</template>

<script>
export default {
  components: {
    ModalError: () => import('@/components/ModalError.vue'),
  },
};
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
