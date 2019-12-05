<template>
  <div class="python3-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp" float>
    <Resize class="python3-resize" :direction="'row'" :lowest="windowHeight==maxHeight" :uppest="windowHeight==minHeight" @dragstart2="onDragStart2" @drag2="onDrag2(-arguments[0])" @dragend2="onDragEnd2"></Resize>
    <NavigationPy :focus="focus" @mouseup2="onMouseUp2"></NavigationPy>
    <div class="python3-test" :style="{height:windowHeight+'px'}">
      Welcome to using ASM Debugger!
      <br />Python3 is developing.
      <br />>>>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';

export default {
  data: function() {
    return {
      minHeight: 18 * 3 + 6,
      maxHeight: 18 * 18 + 6,
      curHeight: 0,
      addHeight: 0,
      focus: false,
      counter: 0
    };
  },
  computed: {
    windowHeight: function() {
      return Math.min(Math.max(this.curHeight + this.addHeight, this.minHeight), this.maxHeight);
    }
  },
  created: function() {
    var curHeight = loadStorage('python3_height', 0);
    this.curHeight = Math.min(Math.max(curHeight, this.minHeight), this.maxHeight);
  },
  mounted: function() {
    keyboard.registerWindow(this);
  },
  destroyed: function() {
    keyboard.unregisterWindow(this);
  },
  methods: {
    requestFocus: function() {
      keyboard.requestFocus(this);
    },
    onFocusChanged: function(value) {
      this.focus = value;
    },
    onMouseUp: function(event) {
      if (event.button == 2) {
        this.onMouseUp2(event);
      }
    },
    onMouseUp2: function(evnet) {
      this.$menu.alert(event);
    },
    onKeyDown: function(event) {
      return false;
    },
    smoothDragTo: function(to) {
      var from = this.curHeight;
      var duration = 147;
      var maxi = Math.ceil((duration * 3) / 50);
      var counter = this.counter;
      requestAnimationFrames(i => {
        if (counter != this.counter) {
          return true;
        }
        var t = ++i / maxi;
        t = 1 - (1 - t) * (1 - t);
        this.curHeight = parseInt((1 - t) * from + t * to);
        return !(i < maxi);
      });
    },
    onDragStart2: function() {
      this.counter++;
    },
    onDrag2: function(delta) {
      this.addHeight = delta;
    },
    onDragEnd2: function(moved) {
      if (moved) {
        this.curHeight = this.windowHeight;
        this.addHeight = 0;
        saveStorage('python3_height', this.curHeight);
      } else {
        var newHeight = this.curHeight != this.minHeight ? this.minHeight : this.maxHeight;
        this.smoothDragTo(newHeight);
        saveStorage('python3_height', newHeight);
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.python3-container {
  position: relative;
  .python3-resize {
    position: absolute;
    left: 0px;
    top: -4px;
    width: 100%;
    height: 8px;
  }
  .python3-test {
    padding-left: 12px;
    line-height: 18px;
    color: @color-text;
    font-size: 12px;
  }
}
</style>
