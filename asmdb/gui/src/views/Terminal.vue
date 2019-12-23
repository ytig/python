<template>
  <div class="terminal-container">
    Welcome to using ASM Debugger!
    <br />Python3 is developing.
    <br />>>> 1 + 1
    <br />2
    <br />>>> 1 + 2
    <br />3
    <br />>>> 1 + 3
    <br />4
    <br />>>>
  </div>
</template>

<script>
import resize from '@/scripts/resize';
//foucs
//width height -> setwinsize
//linux bytes
//input -> writeb 粘贴，中文输入：悬浮
//scroll infinite
export default {
  data: function() {
    return {};
  },
  mounted: function() {
    resize.registerEvent(this);
  },
  destroyed: function() {
    resize.unregisterEvent(this);
  },
  methods: {
    onResize: function() {}
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.terminal-container {
  overflow-y: scroll;
  padding-left: 12px;
  padding-top: 2px;
  padding-right: 12px;
  padding-bottom: 4px;
  line-height: 16px;
  color: @color-text;
  font-size: 12px;
  word-break: break-word;
}
</style>
