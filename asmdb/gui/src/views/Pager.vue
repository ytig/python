<template>
  <div ref="container" class="pager-container">
    <div :style="{left:(0.5-anim.value)*2*36+'px'}">
      <div class="pager-circle" :css-enable="lazySub||(anim.value==0&&canSub)">
        <span>Pre</span>
        <span>↩</span>
      </div>
      <div class="pager-circle" :css-enable="lazyAdd||(anim.value==1&&canAdd)">
        <span>Nxt</span>
        <span>↪</span>
      </div>
    </div>
  </div>
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
    this.histroy.push(deltaY);
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
    var ease_in = Animation.ease_in(250);
    var speed = function(value, target) {
      return ease_in(1 - 2 * Math.abs(value - 0.5), 1);
    };
    return {
      wheeling: new Wheeling(this),
      anim: new Animation(speed, null, 0.5),
      lazySub: false,
      lazyAdd: false
    };
  },
  props: {
    canSub: Boolean,
    canAdd: Boolean
  },
  mounted: function() {
    this.$refs.container.parentNode.addEventListener('wheel', this.onWheel);
  },
  beforeDestroy: function() {
    this.$refs.container.parentNode.removeEventListener('wheel', this.onWheel);
  },
  methods: {
    onWheel: function(event) {
      emptySelection();
      this.wheeling.onWheel(event);
    },
    onWheelDown: function() {
      if (this._isDestroyed) {
        return;
      }
      this.anim.$value(this.anim.value);
      this.lazySub = false;
      this.lazyAdd = false;
    },
    onWheelMove: function(dx) {
      if (this._isDestroyed) {
        return;
      }
      var d = dx / 117;
      this.anim.$value(Math.min(Math.max(this.anim.value + d, 0), 1));
    },
    onWheelUp: function() {
      if (this._isDestroyed) {
        return;
      }
      if (this.anim.value == 0 && this.canSub) {
        this.$emit('delta', -1);
        this.lazySub = true;
      }
      if (this.anim.value == 1 && this.canAdd) {
        this.$emit('delta', 1);
        this.lazyAdd = true;
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
  z-index: 4;
  width: 100%;
  height: 100%;
  overflow: hidden;
  pointer-events: none;
  > div {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    .pager-circle {
      position: relative;
      width: 48px;
      height: 48px;
      border-radius: 999px;
      background: @color-background-dark;
      box-shadow: 0px 2px 6px @color-border-shadow;
      display: flex;
      flex-direction: column;
      justify-content: center;
      padding-top: 2px;
      > span {
        width: 32px;
        text-align: center;
        color: @color-text-darker;
      }
      > span:nth-child(1) {
        font-family: 'Wawati SC';
        font-size: 12px;
      }
      > span:nth-child(2) {
        font-family: 'PingFang SC';
        font-size: 16px;
      }
    }
    .pager-circle[css-enable] {
      > span {
        color: @color-text-menu;
      }
    }
    .pager-circle:first-child {
      left: -52px;
      > span {
        align-self: flex-end;
      }
    }
    .pager-circle:last-child {
      left: 52px;
      > span {
        align-self: flex-start;
      }
    }
  }
}
</style>
