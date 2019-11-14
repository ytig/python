<template>
  <div ref="container" v-show="show" class="editor-container" :style="{left:left+'px',top:top+'px'}">
    <div style="width:100px;height:100px"></div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      left: 0,
      top: 0,
      show: false,
      length: 0,
      placeholder: '',
      listener: null
    };
  },
  methods: {
    alert: function(left, top, length, placeholder, listener) {
      this.left = left;
      this.top = top;
      this.show = true;
      this.length = length;
      this.placeholder = placeholder;
      this.listener = listener;
    },
    close: function() {
      this.show = false;
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.editor-container {
  position: fixed;
  z-index: 7;
  display: inline-block;
  background: @color-background-dark;
  box-shadow: 0px 2px 6px @color-border-shadow;
  padding-top: 4px;
  padding-bottom: 4px;
}
</style>
