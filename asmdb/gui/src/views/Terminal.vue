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
export default {
  data: function() {
    return {};
  },
  mounted: function() {},
  destroyed: function() {},
  methods: {}
};
</script>

<style lang="less">
@import '~@/styles/theme';

.terminal-container {
  overflow-y: scroll;
  padding-left: 12px;
  padding-top: 2px;
  padding-bottom: 4px;
  line-height: 18px;
  color: @color-text;
  font-size: 12px;
}
</style>
