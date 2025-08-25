<template>
  <div
    ref="root"
    class="barchart"
  >
    <svg
      ref="svgEl"
      :width="observedWidth"
      :height="height"
    >
      <g ref="gEl">
        <g
          ref="barsEl"
          class="bars"
          :transform="`translate(${marginLeft},0)`"
        />

        <g
          ref="focusEl"
          class="focus"
          style="visibility: hidden;"
        >
          <circle r="3" />

          <g class="tooltip">
            <rect
              x="0"
              y="0"
              rx="3"
              ry="3"
            />
            <text
              x="5"
              y="5"
            />
          </g>
        </g>

        <rect
          class="overlay"
          :width="observedWidth"
          :height="innerH"
          @mouseenter="onEnter"
          @mousemove="onMove"
          @mouseleave="onLeave"
          @touchmove.prevent="onTouch"
          @touchstart.prevent="onEnter"
          @touchend.prevent="onLeave"
        />

        <g
          ref="axisEl"
          class="axis axis--y"
          :transform="`translate(${marginLeft},0)`"
        />
      </g>
    </svg>
  </div>

  <slot />
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, computed, watchEffect } from 'vue'
import { useI18n } from 'vue-i18n'
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

const { t } = useI18n({ useScope: 'global' })

let centers = []
let xScale, yScale
let resizeObserver = null

const root = ref(null)
const gEl = ref(null)
const svgEl = ref(null)
const axisEl = ref(null)
const barsEl = ref(null)
const focusEl = ref(null)
const observedWidth = ref(0)

const innerH = computed(() => Math.max(0, props.height - 20))

const binned = computed(() => {
  return props.data.slice(0, 9)
})

const marginLeft = computed(() => {
  return d3.max(binned.value, d => d.name.length) * 6.5
})

function render(width, height, data) {
  xScale = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.count)])
    .nice()
    .range([0, width - marginLeft.value])
    .clamp(true)

  yScale = d3.scaleBand()
    .domain(data.map(d => d.name))
    .range([0, height])
    .paddingInner(0.1)

  centers = data.map(d => yScale(d.name) + yScale.bandwidth() / 2)

  const g = d3.select(barsEl.value)
    .selectAll('g.bar')
    .data(data, d => d.name)

  const gEnter = g.enter()
    .append('g')
    .attr('class', 'bar')

  gEnter.append('rect')
    .attr('fill', 'rgb(217, 217, 217)')

  gEnter.append('line')
    .attr('stroke', 'rgb(66, 66, 66)')
    .attr('stroke-width', 2)

  const gAll = gEnter.merge(g)

  gAll.select('rect')
    .attr('x', 0)
    .attr('y', d => yScale(d.name))
    .attr('width', 0)
    .attr('height', yScale.bandwidth())
    .transition()
    .duration(450)
    .ease(d3.easeCubicOut)
    .attr('x', 0)
    .attr('y', d => yScale(d.name))
    .attr('width', d => xScale(d.count))
    .attr('height', yScale.bandwidth())

  gAll.select('line')
    .attr('x1', d => xScale(d.count))
    .attr('x2', d => xScale(d.count))
    .attr('y1', d => yScale(d.name))
    .attr('y2', d => yScale(d.name) + yScale.bandwidth())

  g.exit()
    .transition()
    .duration(300)
    .ease(d3.easeCubicIn)
    .style('opacity', 0)
    .remove()

  const axis = d3.axisLeft(yScale)
    .tickSizeOuter(0)

  d3.select(axisEl.value).call(axis)
}

function onEnter() {
  d3.select(focusEl.value)
    .style('visibility', 'hidden')
    .style('pointer-events', 'none')
}

function onMove(evt) {
  const [, py] = d3.pointer(evt, svgEl.value)
  const height = +innerH.value || 0
  const y = Math.max(0, Math.min(height, py))

  const j = d3.bisect(centers, y)
  const j0 = Math.max(0, j - 1)
  const j1 = Math.min(j, centers.length - 1)
  const i = (y - centers[j0] <= centers[j1] - y) ? j0 : j1  

  const d = binned.value[i]
  const cx = marginLeft.value + xScale(d.count)
  const cy = centers[i]

  const g = d3.select(focusEl.value)
  const circle = g.select('circle')
  const tooltip = g.select('.tooltip')
  const rect = tooltip.select('rect')
  const text = tooltip.select('text')

  g.attr('transform', `translate(${cx},${cy})`)

  const valueText = t('general.objects', { count: d.count })
  text.text(`${d.name}: ${valueText}`)

  const bbox = text.node().getBBox()
  const boxW = Math.ceil(bbox.width) + 10
  const boxH = Math.ceil(bbox.height) + 6

  rect.attr('width', boxW)
    .attr('height', boxH)
    .lower()

  const totalWidth = +observedWidth?.value || 0
  const onRightSide = cx > totalWidth / 2
  const r = +circle.attr('r') || 3

  const tx = (onRightSide ? -1 : 1) * (r + 2) + (onRightSide ? -boxW : 0)
  let ty = -bbox.height / 2

  const bottomY = cy + ty + boxH
  if (bottomY > innerH.value) {
    ty -= (bottomY - innerH.value) + 10
  } else if (cy + ty < 20) {
    ty += 10
  }

  tooltip.attr('transform', `translate(${tx},${ty})`)
  g.style('visibility', 'visible')
}

function onTouch(evt) {
  onMove(evt.touches[0])
}

function onLeave() {
  onEnter()
}

onMounted(() => {
  if (props.width != null) observedWidth.value = props.width

  if (props.width == null && root.value) {
    let raf = 0
    resizeObserver = new ResizeObserver(entries => {
      const { contentRect } = entries[0] ?? {}
      if (!contentRect) return
      const w = Math.floor(contentRect.width || 0)

      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        if (props.width == null && w > 0 && w !== observedWidth.value) {
          observedWidth.value = w
        }
      })
    })
    resizeObserver.observe(root.value)
  }
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect?.()
    resizeObserver = null
  }
})

watchEffect(() => {
  const w = props.width ?? observedWidth.value
  render(w, innerH.value, binned.value)
})
</script>

<style scoped>
.barchart {
  position: relative;
  width: 100%;
}

.overlay {
  fill: transparent;
}

.circle,
.axis--x text,
.tooltip text {
  fill: currentcolor;
}

.axis--x text,
.tooltip text {
  font-size: 10px;
  dominant-baseline: hanging;
}

.tooltip rect {
  fill: #fff
}
</style>