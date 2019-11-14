<template>
  <div ref="container" v-show="show" class="editor-container" :style="{left:left+'px',top:top+'px'}">
    <input ref="input" type="text" :style="{width:inputWidth+'px'}" v-model="text" @input="onInput" @keypress="onKeyPress" @blur="onBlur" />
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
      listener: null,
      text: '',
      realText: ''
    };
  },
  computed: {
    inputWidth: function() {
      return Math.ceil(1 + measureText(this.realText, '12px Menlo'));
    }
  },
  methods: {
    alert: function(left, top, length, placeholder, listener) {
      this.left = left;
      this.top = top;
      this.show = true;
      this.length = length;
      this.placeholder = placeholder;
      this.listener = listener;
      this.text = '';
      this.realText = '';
    },
    close: function() {
      this.show = false;
    },
    onInput: function() {
      this.realText = this.$refs.input.value;
    },
    onKeyPress: function(event) {
      if (event.keyCode == 13) {
        if (this.text) {
          this.listener(parseInt('0x' + this.text));
        }
        this.close();
      }
    },
    onBlur: function() {
      this.close();
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
  > input {
    box-sizing: content-box;
    border-radius: 2px;
    border: 1px solid transparent;
    padding: 3px 3px 1px 20px;
    max-width: 224px;
    font-size: 12px;
    color: @color-text-light;
  }
}
</style>
