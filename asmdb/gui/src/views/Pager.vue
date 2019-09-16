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
    var dx = event.deltaX;
    var dy = event.deltaY;
    this.onWheelMove(dx, dy);
    var counter = ++this.counter;
    setTimeout(() => {
      if (counter == this.counter) {
        this.onWheelUp();
      }
    }, 50);
    this.histroy[this.histroy.length] = [dx, dy, new Date().getTime()];
    if (this.histroy.length >= 4) {
      var isAnim = true;
      var oldSpeedX = Infinity;
      var oldSpeedY = Infinity;
      for (var i = 1; i < this.histroy.length; i++) {
        var deltaTime = this.histroy[i][2] - this.histroy[i - 1][2];
        if (deltaTime < 16 || deltaTime > 24) {
          isAnim = false;
          break;
        }
        var newSpeedX = Math.abs(this.histroy[i][0]) / deltaTime;
        var newSpeedY = Math.abs(this.histroy[i][1]) / deltaTime;
        if (newSpeedX >= oldSpeedX) {
          isAnim = false;
          break;
        }
        oldSpeedX = newSpeedX;
        oldSpeedY = newSpeedY;
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

  onWheelMove(dx, dy) {
    if (this.touching) {
      this.handler.onWheelMove(dx, dy);
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
    onWheelMove: function(dx, dy) {
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
