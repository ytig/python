<template>
  <div class="python3-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Resize class="python3-resize" :direction="'row'" :lowest="windowHeight==maxHeight" :uppest="windowHeight==minHeight" @drag2="onDrag2(-arguments[0])" @dragend2="onDragEnd2"></Resize>
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
      minHeight: 64,
      maxHeight: 200,
      curHeight: 0,
      addHeight: 0,
      focus: false
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
    onDrag2: function(delta) {
      this.addHeight = delta;
    },
    onDragEnd2: function() {
      this.curHeight = this.windowHeight;
      this.addHeight = 0;
      saveStorage('python3_height', this.curHeight);
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
    top: -2px;
    width: 100%;
    height: 4px;
  }
  .python3-test {
    padding-left: 12px;
    line-height: 18px;
    color: @color-text;
    font-size: 12px;
    background: @color-background;
  }
}
</style>
