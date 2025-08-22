<template>
  <div
    ref="root"
    class="histogram"
  >
    TODO
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, computed, watch } from 'vue'
import * as d3 from 'd3'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  height: {
    type: Number,
    default: 125
  },
  width: {
    type: Number,
    default: null
  }
})

let resizeObserver = null

const root = ref(null)
const observedWidth = ref(0)

function render() {
  
}

onMounted(() => {
  if (props.width == null && root.value) {
    resizeObserver = new ResizeObserver(entries => {
      for (const entry of entries) {
        const w = Math.floor(entry.contentRect.width || 0)
        if (w > 0 && w !== observedWidth.value) {
          observedWidth.value = w
          render()
        }
      }
    })
    resizeObserver.observe(root.value)
  } else {
    observedWidth.value = props.width
    render()
  }
})

onBeforeUnmount(() => {
  if (resizeObserver && root.value) {
    resizeObserver.unobserve(root.value)
  }
  resizeObserver = null
})
</script>