<template>
  <v-img
    v-bind="computedProps"
    ref="imageElement"
    v-on:load="loaded"
  >
    <template v-slot:placeholder>
      <slot name="placeholder"></slot>
    </template>
    <div
      v-bind:style="{
        height: image.height + 'px',
        width: image.width + 'px',
        position: 'relative',
        margin: 'auto',
        zIndex: 100,
      }"
    >
      <canvas
        ref="canvas"
        class="canvas"
        @mousedown="onMouseDown"
        @mouseup="onMouseUp"
        @mousemove="onMouseMove"
        @mouseleave="onMouseUp"
        @click="onMouseClick"
        v-click-outside="clickOutside"
      >
      </canvas>
      <v-menu
        :value="menu.show"
        :position-x="menu.x"
        :position-y="menu.y"
        :close-on-click="false"
        transition="fade-transition"
        absolute
        offset-y
      >
        <slot name="context"></slot>
      </v-menu>
    </div>
  </v-img>
</template>

<script>
import { VImg } from 'vuetify/lib';

export default {
  extends: VImg,
  data() {
    return {
      ...VImg.data,
      canvas: null,
      ctx: null,
      roi: null,
      mouse: {
        start: null,
        down: null,
      },
      image: {
        base: null,
        width: 0,
        height: 0,
      },
      menu: {
        show: false,
        x: null,
        y: null,
      },
      client: {
        width: 0,
        height: 0,
      },
    };
  },
  props: {
    ...VImg.props,
    value: Object,
  },
  methods: {
    getScale() {
      const imageHeight = this.image.base.naturalHeight;
      const imageWidth = this.image.base.naturalWidth;
      const scaleHeight = this.client.height / imageHeight;
      const scaleWidth = this.client.width / imageWidth;
      const scale = Math.min(scaleHeight, scaleWidth);
      return {
        height: imageHeight * scale,
        width: imageWidth * scale,
      };
    },
    loaded(src) {
      const image = new Image();
      image.onload = () => {
        if (this.client.height === 0) {
          this.client.height = this.$el.clientHeight;
        }
        if (this.client.width === 0) {
          this.client.width = this.$el.clientWidth;
        }
        const { width, height } = this.getScale();
        if (width > 0 && height > 0) {
          this.image.width = width;
          this.image.height = height;
          this.ctx.canvas.width = width;
          this.ctx.canvas.height = height;
          this.ctx.clearRect(0, 0, width, height);
        }
        this.setROI(this.value);
        this.drawROI();
      }
      image.src = src;
      this.image.base = image;
    },
    computeRect(pos1, pos2) {
      const x = Math.min(pos1.x, pos2.x);
      const y = Math.min(pos1.y, pos2.y);
      return {
        x,
        y,
        width: Math.max(pos1.x, pos2.x) - x,
        height: Math.max(pos1.y, pos2.y) - y,
      };
    },
    drawDefaultRect() {
      this.ctx.clearRect(0, 0, this.image.width, this.image.height);
      this.ctx.fillStyle = 'rgba(189, 189, 189, 0.65)';
      this.ctx.fillRect(0, 0, this.image.width, this.image.height);
    },
    setROI(roi, relative = true) {
      if (roi && !relative) {
        roi = {
          x: roi.x / this.image.width,
          y: roi.y / this.image.height,
          width: roi.width / this.image.width,
          height: roi.height / this.image.height,
        };
      }
      this.roi = roi;
    },
    drawROI() {
      if (this.roi) {
        this.drawDefaultRect();
        let { x, y, width, height } = this.roi;
        x *= this.image.width;
        y *= this.image.height;
        width *= this.image.width;
        height *= this.image.height;
        this.ctx.clearRect(x, y, width, height);
        this.ctx.beginPath();
        this.ctx.rect(x, y, width, height);
        this.ctx.lineWidth = 1;
        this.ctx.strokeStyle = 'rgba(230, 57, 70, 1)';
        this.ctx.stroke();
      }
    },
    clickOutside() {
      this.mouse.down = false;
      this.menu.show = false;
    },
    onMouseClick(evt) {
      evt.preventDefault();
    },
    onMouseDown(evt) {
      evt.preventDefault();
      this.mouse.start = this.mousePos(evt);
      this.mouse.down = true;
      this.menu.show = false;
      if (this.ctx) {
        this.$el.style.cursor = 'crosshair';
        this.drawDefaultRect();
      }
    },
    onMouseUp(evt) {
      if (this.ctx && this.mouse.down) {
        this.mouse.down = false;
        this.$el.style.cursor = 'default';
        const rect = this.computeRect(this.mouse.start, this.mousePos(evt));
        // region of interest is too small
        if (rect.width * rect.height < 20) {
          this.ctx.clearRect(0, 0, this.image.width, this.image.height);
          this.$emit('update', null);
          return;
        }
        this.setROI(rect, false);
        this.drawROI();
        this.$emit('update', this.roi);
        this.menu = {
          show: false,
          x: evt.clientX,
          y: evt.clientY,
        };
        this.$nextTick(() => {
          this.menu.show = true;
        });
      }
    },
    onMouseMove(evt) {
      if (this.ctx && this.mouse.down) {
        const rect = this.computeRect(this.mouse.start, this.mousePos(evt));
        this.setROI(rect, false);
        this.drawROI();
      }
    },
    mousePos({ clientX, clientY }) {
      const rect = this.canvas.getBoundingClientRect();
      const scaleX = this.canvas.width / rect.width;
      const scaleY = this.canvas.height / rect.height;
      return {
        x: (clientX - rect.left) * scaleX,
        y: (clientY - rect.top) * scaleY,
      };
    },
  },
  computed: {
    computedProps() {
      return { ...this.$props };
    },
  },
  watch: {
    src() {
      const { width, height } = this.canvas;
      this.ctx.clearRect(0, 0, width, height);
      this.menu = { show: false, x: null, y: null };
    },
    value(rect) {
      this.setROI(rect);
      this.drawROI();
    },
  },
  mounted() {
    this.canvas = this.$refs.canvas;
    this.ctx = this.canvas.getContext('2d');
  },
};
</script>

<style>
.canvas {
  width: 100%;
  height: 100%;
}
</style>
