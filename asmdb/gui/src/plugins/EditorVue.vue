<template>
  <div ref="container" v-show="show" class="editor-container" :style="{left:left+'px',top:top+'px'}">
    <div style="width:100px;height:100px"></div>
  </div>
</template>

<script>
function getChildIndex(parent, child) {
  while (child) {
    if (child.parentNode == parent) {
      return new Array(...parent.childNodes).indexOf(child);
    }
    child = child.parentNode;
  }
  return -1;
}

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
    },
    onMouseDown: function(event) {
      var intercept = this.show;
      var inner = this.$refs.container == event.target || getChildIndex(this.$refs.container, event.target) >= 0;
      if (!inner) {
        this.close();
      }
      return intercept;
    },
    onKeyDown: function(event) {
      return this.show;
    },
    onWheel: function(event) {
      this.close();
      return false;
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
