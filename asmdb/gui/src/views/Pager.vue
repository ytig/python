<template>
  <div ref="container" class="pager-container"></div>
</template>

<script>
import Animation from '@/scripts/animation';

class Wheeling {
  constructor(handler) {
    this.handler = handler;
    this.touching = false;
  }

  onWheel(event) {
    if (event.cancelable) {
      if (this.touching) {
        this.handler.onWheelUp();
      } else {
        this.touching = true;
      }
      this.handler.onWheelDown();
    }
    if (this.touching) {
      this.handler.onWheelMove(event.deltaX, event.deltaY);
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
    onWheelMove: function(dx, dy) {
      var d = dx / 300;
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
}
</style>
