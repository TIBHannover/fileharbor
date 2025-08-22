<template>
  <div
    ref="root"
    :class="props.class"
    :style="{ height: `${props.height}px` }"
  />

  <slot />
</template>

<script setup>
import { h, onBeforeUnmount, onMounted, ref, computed, watch, nextTick } from 'vue'
import 'leaflet/dist/leaflet.css'
import * as L from 'leaflet'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'
import 'leaflet.markercluster'

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  class: {
    type: String,
    default: null
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

let clusterLayer = null
let resizeObserver = null

const root = ref(null)
const map = ref(null)
const tile = ref(null)
const observedWidth = ref(0)

const points = computed(() => {
  return (props.data || [])
    .filter(d => +d?.lon && +d?.lat)
    .flatMap(d => {
      const out = []
      for (let i = 0; i < d.count; i++) {
        out.push({ ...d })
      }
      return out
    })
})

function makeIcon(name, color = 'primary') {
  const html = `<i class="v-icon mdi ${name} text-${color} notranslate v-icon--size-default"></i>`

  return L.divIcon({
    html,
    iconSize: [24, 24]
  })
}

function buildMarker(d) {
  const lat = +d.lat
  const lon = +d.lon

  const marker = L.marker([lat, lon], {
    icon: makeIcon('mdi-map-marker-outline', 'error')
  })

  if (d?.name) {
    marker.bindTooltip(d?.name, {
      direction: 'top',
      sticky: true
    })
  }

  return marker
}

function fitToData() {
  if (clusterLayer) {
    const bounds = clusterLayer.getBounds?.()
    if (bounds && bounds.isValid()) {
      map.value.fitBounds(bounds, { padding: [20, 20] })
      return
    }
  }
  map.value.fitWorld({ padding: [20, 20] })
}

function render() {
  if (!clusterLayer) {
    clusterLayer = L.markerClusterGroup({
      showCoverageOnHover: false,
      zoomToBoundsOnClick: false,
      spiderfyOnMaxZoom: false,
      chunkedLoading: true,
      animate: true
    })
    clusterLayer.addTo(map.value)
  }

  const markers = points.value.map(buildMarker)
  clusterLayer.addLayers(markers)

  fitToData()
}

onMounted(() => {
  map.value = L.map(root.value, {
    worldCopyJump: true,
    zoomControl: false,
    preferCanvas: true
  })

  tile.value = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}{r}.png', {
    maxZoom: 19,
    attribution: ''
  }).addTo(map.value)

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
  if (map.value) {
    map.value.off()
    map.value.remove()
    map.value = null
  }

  if (clusterLayer) {
    clusterLayer.clearLayers()
    if (map.value) clusterLayer.removeFrom(map.value)
    clusterLayer = null
  }

  if (map.value) {
    map.value.off()
    map.value.remove()
    map.value = null
  }

  tile.value = null

  if (resizeObserver && root.value) {
    resizeObserver.unobserve(root.value)
    resizeObserver.disconnect()
    resizeObserver = null
  }
})

watch(points, () => {
  render()
})

watch(
  () => [props.height, props.width],
  async () => {
    await nextTick()
    if (map.value) {
      map.value.invalidateSize()
      if (clusterLayer) fitToData()
    }
  }
)
</script>

<style>
.leaflet-container .leaflet-control-attribution {
  display: none
}

.leaflet-container .leaflet-tile {
  filter: grayscale(1) brightness(1);
}

.leaflet-container.leaflet-div-icon {
  width: auto;
  height: auto;
  font-size: 1rem;
  border: none;
  background: none;
}

.leaflet-container .marker-cluster-small,
.leaflet-container .marker-cluster-small div,
.leaflet-container .marker-cluster-medium,
.leaflet-container .marker-cluster-medium div,
.leaflet-container .marker-cluster-large,
.leaflet-container .marker-cluster-large div {
  background-color: rgba(230 57 70 / 60%);
}
</style>