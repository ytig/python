<template>
  <div ref="container" class="pager-container" :style="{left:scrollX+'px'}"></div>
</template>

<script>
import Animation from '@/scripts/animation';

class Wheeling {
  constructor(handler, reverse) {
    this.handler = handler;
    this.reverse = reverse;
    this.touching = false;
    this.counter = 0;
    this.histroy = [];
  }

  onWheel(event) {
    if (!this.reverse) {
      var deltaX = event.deltaX;
      var deltaY = event.deltaY;
    } else {
      var deltaX = event.deltaY;
      var deltaY = event.deltaX;
    }
    if (event.cancelable) {
      this.onWheelDown();
      this.histroy.splice(0, this.histroy.length);
    }
    this.onWheelMove(deltaX);
    if (Math.abs(deltaY) > 3) {
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
    this.histroy[this.histroy.length] = deltaY;
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

  onWheelMove(delta) {
    if (this.touching) {
      this.handler.onWheelMove(delta);
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
      anim: new Animation(
        (value, target) => {
          var speed = (Math.pow(Math.abs(target - value), this.power) * Math.pow(0.1, 1 - this.power)) / ((1 - this.power) * this.duration);
          return Math.max(speed, 1 / (60 * 60 * 1000));
        },
        (value, target) => {
          this.scrollX = this.toCoordinate(value);
        },
        0.5
      ),
      range: 260,
      touch: 0.346,
      power: 0.75,
      duration: 224,
      scrollX: 0
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
      var scrollX = this.toCoordinate(this.anim.value);
      var negative = scrollX < 0 || (scrollX == 0 && dx > 0);
      if (negative) {
        dx *= -1;
        scrollX *= -1;
      }
      var x = this.range * this.touch * Math.pow(this.range / (this.range - scrollX), 1 / this.touch) - this.range * this.touch;
      x = x * (x - dx) < 0 ? 0 : x - dx;
      scrollX = this.range - this.range * Math.pow(1 + x / (this.range * this.touch), -this.touch);
      if (negative) {
        scrollX *= -1;
      }
      this.anim.$value(this.toValue(scrollX));
    },
    onWheelUp: function() {
      if (this.anim.value == 0 && this.canSub) {
        this.$emit('delta', -1);
      }
      if (this.anim.value == 1 && this.canAdd) {
        this.$emit('delta', 1);
      }
      this.anim.$target(0.5);
    },
    toCoordinate: function(value) {
      return (value - 0.5) * 2 * this.range;
    },
    toValue: function(coordinate) {
      return coordinate / (2 * this.range) + 0.5;
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
