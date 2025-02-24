<template>
  <div id="network">
    <ModalItem
      v-model="itemDialog"
      v-if="entries.length"
      :entry="entries[0]"
      :isFirst="true"
      :isLast="true"
    />

    <ModalGrid
      v-model="gridDialog"
      v-if="entries.length"
      :entries="entries"
    />

    <div class="canvas"></div>
  </div>
</template>

<script>
import hull from 'hull.js';
import clustering from 'density-clustering';
import { Network } from 'vis-network/peer';
import { inflatePolygon, getCentroid } from '@/plugins/helpers';
import ModalItem from '@/components/ModalItem.vue';
import ModalGrid from '@/components/ModalGrid.vue';

const Colors = [
  '#F44336', '#2196F3', '#8BC34A', '#FF5722', '#E91E63',
  '#03A9F4', '#CDDC39', '#795548', '#9C27B0', '#00BCD4',
  '#FFEB3B', '#607D8B', '#673AB7', '#009688', '#FFC107',
  '#9E9E9E', '#3F51B5', '#4CAF50', '#FF9800', '#000000',
];
export default {
  props: ['data'],
  data() {
    return {
      itemDialog: false,
      gridDialog: false,
      clickTime: 0,
      entries: [],
      state: {
        highlight: true,
        drag: false,
        grid: false,
      },
      options: {
        physics: false,
        interaction: {
          navigationButtons: true,
          multiselect: true,
          dragNodes: false,
          hover: true,
        },
      },
      focusOptions: {
        scale: 25,
        animation: {
          easingFunction: 'easeInOutQuad',
          duration: 1000,
        },
      },
    };
  },
  computed: {
    settings() {
      return this.$store.state.api.settings;
    },
    drawerSettings() {
      return this.$store.state.user.drawer.settings;
    },
  },
  methods: {
    init() {
      this.container = document.querySelector('#network .canvas');
      this.container.oncontextmenu = function () { return false; };
      this.container.addEventListener('mousemove', this.onMouseMove);
      this.container.addEventListener('mousedown', this.onMouseDown);
      this.container.addEventListener('mouseup', this.onMouseUp);
      this.network = new Network(this.container);
      this.network.setOptions(this.options);
      this.canvas = this.network.canvas.frame.canvas;
      this.ctx = this.canvas.getContext('2d');
      this.network.on('hoverNode', function () {
        this.canvas.body.container.style.cursor = 'pointer';
      });
      this.network.on('blurNode', function () {
        this.canvas.body.container.style.cursor = 'default';
      });
      this.network.on('afterDrawing', () => {
        if (this.state.drag) {
          this.drawSelection();
        }
        if (this.state.highlight) {
          this.drawHulls();
        }
      });
      this.network.on('click', this.onClick);
      this.network.on('doubleClick', this.onDoubleClick);
      window.addEventListener('resize', this.onResize);
      const rObs = new ResizeObserver(this.drawNodes);
      rObs.observe(this.container);
    },
    getSize() {
      const network = document.querySelector('#network');
      if (network) {
        const { bottom } = network.getBoundingClientRect();
        let { clientHeight } = network;
        const { clientWidth } = network;
        if (bottom >= window.innerHeight) {
          clientHeight -= (bottom - window.innerHeight + 6);
        }
        return [clientWidth, clientHeight - 1];
      }
      return [0, 0];
    },
    onClick({ nodes }) {
      const t0 = new Date();
      if (t0 - this.clickTime > 250) {
        setTimeout(() => {
          if (t0 - this.clickTime > 250) {
            if (nodes && nodes.length === 1) {
              const item = this.nodes.find(
                ({ id }) => nodes.includes(id),
              );
              this.entries = [item.entry];
              this.itemDialog = true;
            }
          }
        }, 250);
      }
    },
    onDoubleClick({ nodes }) {
      this.clickTime = new Date();
      if (nodes && nodes.length === 1) {
        this.network.focus(nodes[0], this.focusOptions);
      }
    },
    onResize() {
      if (this.network) {
        this.network.setOptions({
          height: `${this.getSize()[1]}px`,
        });
      }
    },
    onMouseDown({ button, pageX, pageY }) {
      if (this.network && button === 2) {
        const offset = this.container.getBoundingClientRect();
        this.rect = {
          startX: pageX - offset.left,
          startY: pageY - offset.top,
          endX: pageX - offset.left,
          endY: pageY - offset.top,
        };
        this.container.style.cursor = 'crosshair';
        this.state.drag = true;
      }
    },
    onMouseUp({ button }) {
      if (this.network && button === 2) {
        this.container.style.cursor = 'default';
        this.state.drag = false;
        this.network.redraw();
        this.selectNodes();
      }
    },
    onMouseMove({ pageX, pageY }) {
      if (this.network && this.state.drag) {
        const offset = this.container.getBoundingClientRect();
        this.rect.endX = pageX - offset.left;
        this.rect.endY = pageY - offset.top;
        this.network.redraw();
      }
    },
    drawSelection() {
      const start = this.toCanvas(this.rect.startX, this.rect.startY);
      const end = this.toCanvas(this.rect.endX, this.rect.endY);
      const w = end.x - start.x;
      const h = end.y - start.y;
      this.ctx.setLineDash([]);
      this.ctx.fillStyle = 'rgba(29, 53, 87, 0.25)';
      this.ctx.fillRect(start.x, start.y, w, h);
    },
    createHulls() {
      this.hulls = {};
      this.centroids = {};
      if (this.nodes) {
        let groups = this.nodes.map(({ group }) => group);
        groups = [...new Set(groups)];
        if (groups.length > 1) {
          const dbscan = new clustering.DBSCAN();
          const f = Math.min(...this.getSize()) / 500;
          groups.forEach((groupID) => {
            const entryPoints = this.nodes.filter(({ group }) => {
              return group === groupID;
            }).map(({ x, y }) => [x, y]);
            const clusters = dbscan.run(entryPoints, f * 20, 1);
            clusters.sort((a, b) => b.length - a.length);
            clusters.forEach((cluster, index) => {
              if (cluster.length > 3) {
                const clusterPoints = entryPoints.filter((obj, index) => {
                  return cluster.includes(index);
                });
                const x = clusterPoints.map(([x]) => x);
                const nX = [...new Set(x)].length;
                const y = clusterPoints.map(([, y]) => y);
                const nY = [...new Set(y)].length;
                if (nX > 1 && nY > 1) {
                  let hullPoints = hull(clusterPoints, f * 50);
                  hullPoints = inflatePolygon(hullPoints, f * 10);
                  if (index === 0) {
                    this.centroids[groupID] = getCentroid(hullPoints);
                  }
                  if (this.hulls[groupID] instanceof Array) {
                    this.hulls[groupID].push(hullPoints);
                  } else {
                    this.hulls[groupID] = [hullPoints];
                  }
                }
              }
            });
          });
        }
      }
    },
    drawHulls() {
      if (this.hulls) {
        Object.keys(this.hulls).forEach((groupID) => {
          this.hulls[groupID].forEach((hullPoints) => {
            this.ctx.globalAlpha = 0.25;
            this.ctx.fillStyle = Colors[groupID];
            this.ctx.beginPath();
            hullPoints.forEach(([x, y], index) => {
              if (index === 0) {
                this.ctx.moveTo(x, y);
              } else {
                this.ctx.lineTo(x, y);
              }
            });
            this.ctx.closePath();
            this.ctx.fill();
          });
        });
      }
      if (this.centroids) {
        const f = Math.min(...this.getSize()) / 500;
        Object.keys(this.centroids).forEach((groupID) => {
          const [xC, yC] = this.centroids[groupID];
          this.ctx.globalAlpha = 1;
          this.ctx.textAlign = 'center';
          this.ctx.textBaseline = 'middle';
          this.ctx.font = `${f * 30}px Roboto, sans-serif`;
          this.ctx.lineWidth = 5;
          this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.85)';
          this.ctx.fillStyle = Colors[groupID];
          this.ctx.strokeText(parseInt(groupID, 10) + 1, xC, yC);
          this.ctx.fillText(parseInt(groupID, 10) + 1, xC, yC);
        });
      }
    },
    drawNodes() {
      const minSize = Math.min(...this.getSize());
      let boxSize = 0;
      const { grid } = this.state;
      if (grid) {
        const x = this.data.map(
          ({ coordinates }) => coordinates[0],
        );
        const nX = [...new Set(x)].length;
        const y = this.data.map(
          ({ coordinates }) => coordinates[1],
        );
        const nY = [...new Set(y)].length;
        boxSize = minSize / Math.max(nX, nY);
      } else {
        const { settings } = this.$store.state.api;
        if (!settings) settings.layout = { itemSize: 0 };
        boxSize = (settings.layout.itemSize + 8) * 2;
      }
      this.nodes = this.data.map((entry) => {
        return {
          id: entry.id,
          shape: 'custom',
          image: entry.preview,
          group: entry.cluster,
          x: entry.coordinates[0] * minSize,
          y: entry.coordinates[1] * minSize,
          entry,
          ctxRenderer: ({ ctx, x, y }) => {
            const img = new Image();
            img.src = entry.preview;
            let minImgSize = img.width;
            let maxImgSize = img.height;
            if (img.width > img.height) {
              minImgSize = img.height;
              maxImgSize = img.width;
            }
            return {
              drawNode() {
                if (grid) {
                  ctx.drawImage(
                    img,
                    (img.width - minImgSize) / 2,
                    (img.height - minImgSize) / 2,
                    minImgSize,
                    minImgSize,
                    x - boxSize / 2,
                    y - boxSize / 2,
                    boxSize,
                    boxSize,
                  );
                  if (entry.cluster > 0 || entry.distance > 0) {
                    ctx.fillStyle = Colors[entry.cluster];
                    ctx.beginPath();
                    ctx.arc(
                      x + boxSize / 2 - boxSize / 5,
                      y - boxSize / 2 + boxSize / 5,
                      boxSize / 7,
                      0,
                      2 * Math.PI,
                    );
                    ctx.fill();
                  }
                } else {
                  const width = img.width / maxImgSize;
                  const height = img.height / maxImgSize;
                  ctx.drawImage(
                    img,
                    x - (width * boxSize) / 2,
                    y - (height * boxSize) / 2,
                    width * boxSize,
                    height * boxSize,
                  );
                  if (entry.cluster > 0 || entry.distance > 0) {
                    ctx.fillStyle = Colors[entry.cluster];
                    ctx.beginPath();
                    ctx.arc(
                      x + (width * boxSize) / 2 - boxSize / 5,
                      y - (height * boxSize) / 2 + boxSize / 5,
                      boxSize / 7,
                      0,
                      2 * Math.PI,
                    );
                    ctx.fill();
                  }
                }
              },
              nodeDimensions: {
                width: boxSize,
                height: boxSize,
              },
            };
          },
        };
      });
      this.network.setData({ nodes: this.nodes });
      this.createHulls();
      this.onResize();
    },
    selectNodes() {
      const start = this.toCanvas(this.rect.startX, this.rect.startY);
      const end = this.toCanvas(this.rect.endX, this.rect.endY);
      const [startX, endX] = this.correctRange(start.x, end.x);
      const [startY, endY] = this.correctRange(start.y, end.y);
      const selected = this.nodes.filter(({ x, y }) => {
        return x >= startX && x <= endX && y >= startY && y <= endY;
      });
      this.entries = selected.map(({ entry }) => entry);
      this.gridDialog = true;
    },
    toCanvas(domX, domY) {
      const values = { x: domX, y: domY };
      return this.network.DOMtoCanvas(values);
    },
    correctRange(x, y) {
      return x < y ? [x, y] : [y, x];
    },
  },
  watch: {
    data() {
      this.drawNodes();
    },
    settings: {
      handler({ layout, cluster }) {
        this.state.highlight = cluster.highlight;
        this.state.grid = layout.viewGrid;
        this.drawNodes();
      },
      deep: true,
    },
    drawerSettings() {
      setTimeout(() => {
        this.onResize();
      }, 250);
    },
  },
  created() {
    const { settings } = this.$store.state.api;
    if (settings && Object.keys(settings).length) {
      if (
        this.keyInObj('cluster', settings)
        && this.keyInObj('highlight', settings.cluster)
      ) {
        this.state.highlight = settings.cluster.highlight;
      }
      if (
        this.keyInObj('layout', settings)
        && this.keyInObj('viewGrid', settings.layout)
      ) {
        this.state.grid = settings.layout.viewGrid;
      }
    }
  },
  mounted() {
    this.init();
  },
  components: {
    ModalItem,
    ModalGrid,
  },
};
</script>

<style>
#network {
  height: 100%;
  width: 100%;
}

#network .vis-network {
  background-color: #e0e0e0;
}

#network .vis-network:focus {
  outline: none;
}

.vis-network .vis-navigation {
  position: absolute;
  bottom: 10px;
  left: 10px;
}

.vis-network .vis-navigation .vis-button.vis-up,
.vis-network .vis-navigation .vis-button.vis-down,
.vis-network .vis-navigation .vis-button.vis-left,
.vis-network .vis-navigation .vis-button.vis-right,
.vis-network .vis-navigation .vis-button.vis-zoomIn,
.vis-network .vis-navigation .vis-button.vis-zoomOut,
.vis-network .vis-navigation .vis-button.vis-zoomExtends {
  background-image: none !important;
}

.vis-network .vis-navigation .vis-button:hover {
  box-shadow: none !important;
}

.vis-button {
  margin-top: 2px;
}

.vis-button:after {
  font: normal normal normal 24px/1 Material Design Icons;
  -webkit-font-smoothing: antialiased;
  text-rendering: auto;
  font-size: 24px;
  line-height: 1;
}

.vis-button:hover:after {
  cursor: pointer;
}

.vis-button.vis-zoomIn:after {
  content: "\F06ED";
}

.vis-button.vis-zoomOut:after {
  content: "\F06EC";
}

.vis-button.vis-zoomExtends:after {
  content: "\F0293";
}
</style>
