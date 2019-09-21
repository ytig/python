<template>
  <div ref="container" class="pager-container" :style="{left:(anim.value-0.5)*100+'px'}"></div>
</template>

<script>
import Animation from '@/scripts/animation';

class Wheeling {
  constructor(handler) {
    this.handler = handler;
    this.touching = false;
    this.counter = 0;
    this.histroy = [];
  }

  onWheel(event) {
    if (event.cancelable) {
      this.onWheelDown();
      this.histroy.splice(0, this.histroy.length);
    }
    this.onWheelMove(event.deltaX);
    if (Math.abs(event.deltaY) > 3) {
      this.onWheelUp();
    }
    var counter = ++this.counter;
    setTimeout(() => {
      if (counter == this.counter) {
        this.onWheelUp();
      }
    }, 50);
    const frameStart = 12;
    const frameLength = 4;
    this.histroy[this.histroy.length] = event.deltaY;
    if (this.histroy.length >= frameStart + frameLength) {
      var isAnim = true;
      for (var i = frameStart; i < this.histroy.length; i++) {
        if (this.histroy[i] != 0) {
          isAnim = false;
          break;
        }
      }
      if (isAnim) {
        this.onWheelUp();
      }
      this.histroy.splice(0, 1);
    }
  }

  onWheelDown() {
    this.onWheelUp();
    this.touching = true;
    this.handler.onWheelDown();
  }

  onWheelMove(dx) {
    if (this.touching) {
      this.handler.onWheelMove(dx);
    }
  }

  onWheelUp() {
    if (this.touching) {
      this.handler.onWheelUp();
      this.touching = false;
    }
  }
}

export default {
  data: function() {
    return {
      wheeling: new Wheeling(this),
      anim: new Animation(1 / 250, null, 0.5)
    };
  },
  props: {
    canSub: Boolean,
    canAdd: Boolean
  },
  mounted: function() {
    this._parent = this.$refs.container.parentNode;
    this._parent.addEventListener('wheel', this.onWheel);
  },
  destroyed: function() {
    this._parent.removeEventListener('wheel', this.onWheel);
    this._parent = null;
  },
  methods: {
    onWheel: function(event) {
      this.wheeling.onWheel(event);
    },
    onWheelDown: function() {
      this.anim.$value(this.anim.value);
    },
    onWheelMove: function(dx) {
      var d = dx / 250;
      this.anim.$value(Math.min(Math.max(this.anim.value + d, 0), 1));
    },
    onWheelUp: function() {
      if (this.anim.value == 0 && this.canSub) {
        this.$emit('delta', -1);
      }
      if (this.anim.value == 1 && this.canAdd) {
        this.$emit('delta', 1);
      }
      this.anim.$target(0.5);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.pager-container {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: #ffffff44;
}
</style>
