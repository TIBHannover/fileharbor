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
          <rect
            class="bg"
            :width="observedWidth"
            :height="observedHeight"
          />

          <g
            ref="imagesEl"
            class="images"
          />
        </g>
      </svg>
    </div>
  </div>

  <slot />
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, computed, watch } from 'vue'
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
    default: 16
  }
})

let xScale, yScale
let resizeObserver = null

const root = ref(null)
const gEl = ref(null)
const svgEl = ref(null)
const imagesEl = ref(null)

const observedWidth = ref(0)
const observedHeight = ref(200)

const items = computed(() => {
  const arr = []
  for (const d of (props.entries)) {
    const coords = d?.coordinates
    if (!Array.isArray(coords) || coords.length < 2) continue
    const x = Number(coords[0])
    const y = Number(coords[1])
    if (!Number.isFinite(x) || !Number.isFinite(y)) continue

    const img = (props.imgPref === 'preview' ? d?.preview : d?.path) ?? d?.preview ?? d?.path
    if (!img) continue

    arr.push({
      id: d.id,
      x, y,
      img,
      raw: d
    })
  }
  return arr
})

function onItemselect() {
  
}

function render() {
  xScale = d3.scaleLinear()
    .domain(d3.extent(items.value, d => d.x))
    .range([0, observedWidth.value])

  yScale = d3.scaleLinear()
    .domain(d3.extent(items.value, d => d.y))
    .range([0, observedHeight.value])

  const sel = d3.select(imagesEl.value)
    .selectAll('image')
    .data(items.value, d => d.id)

  const enter = sel.enter().append('image')
    .attr('href', d => d.img)
    .attr('clip-path', 'url(#round)')
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
        .attr('x', xScale(d.x) - props.pointSize * 1.2)
        .attr('y', yScale(d.y) - props.pointSize * 1.2)
        .transition().duration(300)
        .attr('width', props.pointSize * 2)
        .attr('height', props.pointSize * 2)
        .attr('x', xScale(d.x) - props.pointSize)
        .attr('y', yScale(d.y) - props.pointSize)

      onItemselect(d.raw)
    })

  enter.merge(sel)
    .attr('width', props.pointSize * 2)
    .attr('height', props.pointSize * 2)
    .attr('x', d => xScale(d.x) - props.pointSize)
    .attr('y', d => yScale(d.y) - props.pointSize)

  sel.exit().remove()
}

onMounted(() => {
  if ((props.width == null || props.height == null) && root.value) {
    resizeObserver = new ResizeObserver(entries => {
      for (const { contentRect } of entries) {
        const w = Math.floor(contentRect.width || 0)
        const h = Math.floor(contentRect.height || 0)
        let changed = false

        if (props.width == null && w > 0 && w !== observedWidth.value) {
          observedWidth.value = w
          changed = true
        }
        if (props.height == null && h > 0 && h !== observedHeight.value) {
          observedHeight.value = h
          changed = true
        }
        if (changed) render()
      }
    })
    resizeObserver.observe(root.value)
  } else {
    if (props.width != null) observedWidth.value = props.width
    if (props.height != null) observedHeight.value = props.height
    render()
  }
})

onBeforeUnmount(() => {
  if (resizeObserver && root.value) {
    resizeObserver.unobserve(root.value)
  }
  resizeObserver = null
})

watch(items, () => {
  render()
})

watch(
  () => [items, props.height, props.width],
  () => render(),
)
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
}

.bg {
  fill: rgba(217 217 217 / 30%);
}
</style>