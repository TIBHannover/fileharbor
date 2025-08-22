<template>
  <div
    ref="root"
    class="histogram"
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
          class="axis axis--x"
          :transform="`translate(0, ${innerH})`"
        />
      </g>
    </svg>
  </div>

  <slot />
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref, computed, watch } from 'vue'
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
  },
  binSize: {
    type: Number,
    default: 10
  },
  maxUnderRatio: {
    type: Number,
    default: 0.02
  }
})

const emit = defineEmits([
  'updateYears'
])

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
  const totals = new Map()
  for (const item of props.data) {
    const y = Number(item?.name)
    const v = Number(item?.count)
    if (Number.isFinite(y) && Number.isFinite(v)) {
      totals.set(y, (totals.get(y) ?? 0) + v)
    }
  }

  const under = [...totals.keys()].filter(y => y <= 1000)
  const ratioUnder = under.length / (totals.size)
  if (ratioUnder <= props.maxUnderRatio) {
    for (const y of under) totals.delete(y)
  }

  const minY = Math.min(...totals.keys())
  const maxY = Math.max(...totals.keys())

  emit('updateYears', [minY, maxY])

  const start = Math.floor(minY / 100) * 100 - 40
  const end = Math.floor(maxY / 100) * 100 + 40
  const count = Math.max(0, Math.ceil((end - start) / props.binSize))

  const out = Array.from({ length: count }, (_, i) => {
    const s = start + i * props.binSize
    return { start: s, end: s + props.binSize, sum: 0 }
  })

  for (const [year, sum] of totals) {
    const idx = Math.floor((year - start) / props.binSize)
    if (idx >= 0 && idx < out.length) out[idx].sum += sum
  }

  return out
})

function render() {
  const data = binned.value
  if (!data.length) return

  xScale = d3.scaleBand()
    .domain(data.map(b => b.start))
    .range([0, observedWidth.value])
    .paddingInner(0.05)
    .paddingOuter(0)

  yScale = d3.scaleLinear()
    .domain([0, d3.max(data, d => d.sum) || 1])
    .nice()
    .range([innerH.value, 0])
    .clamp(true)

  centers = data.map(d => (xScale(d.start) ?? 0) + xScale.bandwidth() / 2)

  const g = d3.select(barsEl.value)
    .selectAll('g.bar')
    .data(data, d => d.start)

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
    .attr('x', d => xScale(d.start))
    .attr('width', xScale.bandwidth())
    .attr('y', innerH.value)
    .attr('height', 0)
    .transition()
    .duration(450)
    .ease(d3.easeCubicOut)
    .attr('y', d => yScale(d.sum))
    .attr('height', d => innerH.value - yScale(d.sum))

  gAll.select('line')
    .attr('x1', d => xScale(d.start))
    .attr('x2', d => (xScale(d.start) ?? 0) + xScale.bandwidth())
    .attr('y1', d => yScale(d.sum))
    .attr('y2', d => yScale(d.sum))

  g.exit()
    .transition()
    .duration(300)
    .ease(d3.easeCubicIn)
    .style('opacity', 0)
    .remove()

  const minYear = data[0].start
  const maxYear = data[data.length - 1].end

  const steps = [50, 100, 200, 500]
  let step = steps[steps.length - 1]
  for (const s of steps) {
    if ((maxYear - minYear) / s <= 10) {
      step = s
      break
    }
  }

  const start = Math.ceil(minYear / step) * step
  const end = Math.floor(maxYear / step) * step
  const ticks = d3.range(start, end + 1, step)

  const axis = d3.axisBottom(xScale)
    .tickValues(ticks)
    .tickFormat(d3.format('d'))
    .tickSizeOuter(0)

  d3.select(axisEl.value).call(axis)
}

function onEnter() {
  d3.select(focusEl.value)
    .style('visibility', 'hidden')
    .style('pointer-events', 'none')
}

function onMove(evt) {
  const [px] = d3.pointer(evt, svgEl.value)
  const width = +observedWidth?.value || 0
  const x = Math.max(0, Math.min(width, px))

  const j = d3.bisect(centers, x)
  const j0 = Math.max(0, j - 1)
  const j1 = Math.min(j, centers.length - 1)
  const i = (x - centers[j0] <= centers[j1] - x) ? j0 : j1  

  const d = binned.value[i]
  const cx = centers[i]
  const cy = yScale(d.sum)

  const g = d3.select(focusEl.value)
  const circle = g.select('circle')
  const tooltip = g.select('.tooltip')
  const rect = tooltip.select('rect')
  const text = tooltip.select('text')

  g.attr('transform', `translate(${cx},${cy})`)

  const rangeText = `${d.start}–${d.end - 1}`;
  const valueText = t('general.objects', { count: d.sum })
  text.text(`${rangeText}: ${valueText}`)

  const bbox = text.node().getBBox()
  const boxW = Math.ceil(bbox.width) + 10
  const boxH = Math.ceil(bbox.height) + 6

  rect.attr('width', boxW)
    .attr('height', boxH)
    .lower()

  const onRightSide = x > width / 2
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

watch(
  () => [binned, props.height, props.width],
  () => render(),
)
</script>

<style scoped>
.histogram {
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