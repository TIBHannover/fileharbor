<template>
  <div class="container">
    <div
      ref="root"
      class="canvas"
    >
      <svg
        ref="svgEl"
        :width="observedWidth"
        :height="observedHeight"
      >
        <g ref="gEl">
          <g
            ref="imagesEl"
            class="images"
          />
        </g>
      </svg>
    </div>
  </div>

  <slot />

  <ResourceDialog
    v-if="selectedItem"
    v-model="dialog"
    :item="selectedItem"
  />
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, computed, watchEffect } from 'vue'
import ResourceDialog from '@/components/dialogs/ResourceDialog.vue'
import * as d3 from 'd3'

const props = defineProps({
  entries: {
    type: Array,
    required: true
  },
  height: {
    type: Number,
    default: null
  },
  width: {
    type: Number,
    default: null
  },
  pointSize: {
    type: Number,
    default: 8
  }
})

let resizeObserver = null

const root = ref(null)
const gEl = ref(null)
const svgEl = ref(null)
const imagesEl = ref(null)

const observedWidth = ref(0)
const observedHeight = ref(0)

const items = computed(() => {
  const arr = []
  for (const d of props.entries) {
    const coords = d?.coordinates
    arr.push({
      x: Number(coords[0]),
      y: Number(coords[1]),
      ...d
    })
  }
  return arr
})

const selectedItem = ref(null)
const dialog = ref(false)
function onItemSelect(item) {
  selectedItem.value = item
  dialog.value = true
}

function render(width, height, data) {
  const xScale = d3.scaleLinear()
    .domain(d3.extent(data, d => d.x))
    .range([0, width])

  const yScale = d3.scaleLinear()
    .domain(d3.extent(data, d => d.y))
    .range([0, height])

  const sel = d3.select(imagesEl.value)
    .selectAll('image')
    .data(data, d => d.id)

  sel.join(
    enter => enter.append('image')
      .attr('href', d => d.preview)
      .attr('width', props.pointSize * 2)
      .attr('height', props.pointSize * 2)
      .attr('x', d => xScale(d.x) - props.pointSize)
      .attr('y', d => yScale(d.y) - props.pointSize)
      .style('cursor', 'pointer')
      .on('click', (event, d) => {
        const node = d3.select(event.currentTarget)
        node.transition().duration(300)
          .attr('width', props.pointSize * 2.4)
          .attr('height', props.pointSize * 2.4)
          .transition().duration(300)
          .attr('width', props.pointSize * 2)
          .attr('height', props.pointSize * 2)

        onItemSelect(d)
      }),
    update => update
      .attr('width', props.pointSize * 2)
      .attr('height', props.pointSize * 2)
      .attr('x', d => xScale(d.x) - props.pointSize)
      .attr('y', d => yScale(d.y) - props.pointSize),
    exit => exit.remove()
  )
}

function initZoom() {
  const zoomBehavior = d3.zoom()
    .scaleExtent([0.75, 10])
    .on("zoom", (event) => {
      d3.select(gEl.value).attr("transform", event.transform)
    })
  d3.select(svgEl.value).call(zoomBehavior)
}

onMounted(() => {
  if (props.width != null) observedWidth.value = props.width
  if (props.height != null) observedHeight.value = props.height

  if ((props.width == null || props.height == null) && root.value) {
    let raf = 0
    resizeObserver = new ResizeObserver(entries => {
      const { contentRect } = entries[0] ?? {}
      if (!contentRect) return
      const w = Math.floor(contentRect.width || 0)
      const h = Math.floor(contentRect.height || 0)

      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        if (props.width == null && w > 0 && w !== observedWidth.value) {
          observedWidth.value = w
        }
        if (props.height == null && h > 0 && h !== observedHeight.value) {
          observedHeight.value = h
        }
      })
    })
    resizeObserver.observe(root.value)
  }

  initZoom()
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect?.()
    resizeObserver = null
  }
})

watchEffect(() => {
  const w = props.width ?? observedWidth.value
  const h = props.height ?? observedHeight.value
  render(w, h, items.value)
})
</script>

<style scoped>
.container {
  width: calc(100% + 16px);
  height: calc(100% + 16px);
  margin: -8px;
}

.canvas {
  width: 100%;
  height: 100%;
  background: rgba(217 217 217 / 30%);
}
</style>