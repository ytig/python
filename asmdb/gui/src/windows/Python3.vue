<template>
  <div class="python3-container">
    <Resize class="python3-resize" :direction="'row'" @drag2="onDrag2" @dragend2="onDragEnd2"></Resize>
    <div class="python3-test" :style="{height:windowHeight+'px'}">
      Welcome to using ASM Debugger!
      <br />Python3 is developing.
      <br />>>>
    </div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      minHeight: 64,
      maxHeight: 200,
      curHeight: 64,
      addHeight: 0
    };
  },
  computed: {
    windowHeight: function() {
      return Math.min(Math.max(this.curHeight + this.addHeight, this.minHeight), this.maxHeight);
    }
  },
  methods: {
    onDrag2: function(delta) {
      this.addHeight = -delta;
    },
    onDragEnd2: function() {
      this.curHeight = this.windowHeight;
      this.addHeight = 0;
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
    padding-top: 6px;
    padding-left: 12px;
    line-height: 18px;
    color: @color-text;
    font-size: 12px;
  }
}
</style>
