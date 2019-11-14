<template>
  <div ref="container" v-show="show" class="editor-container" :style="{left:left+'px',top:top+'px'}">
    <span>0x</span>
    <input ref="input" type="text" :style="{width:inputWidth+'px'}" :placeholder="placeholder" @input="onInput" @compositionstart="onCompositionStart" @compositionend="onCompositionEnd" @keypress="onKeyPress" @blur="onBlur" />
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
      composition: false,
      text: ''
    };
  },
  computed: {
    inputWidth: function() {
      var w1 = measureText(this.text, '12px Menlo');
      var w2 = measureText(this.placeholder, '12px Menlo');
      return Math.ceil(1 + Math.max(w1, w2));
    }
  },
  methods: {
    alert: function(left, top, length, placeholder, listener) {
      this.left = left - 1;
      this.top = top - 1;
      this.show = true;
      this.length = length;
      this.placeholder = placeholder;
      this.listener = listener;
      this.composition = false;
      this.text = '';
      this.$refs.input.value = '';
      this.$nextTick(function() {
        this.$refs.input.focus();
      });
    },
    close: function() {
      this.show = false;
    },
    onInput: function() {
      if (!this.composition) {
        this.onCompositionEnd();
      }
      this.text = this.$refs.input.value;
    },
    onCompositionStart: function() {
      this.composition = true;
    },
    onCompositionEnd: function() {
      this.composition = false;
      var input = this.$refs.input;
      input.value = input.value.replace(/[^0-9a-f]/g, '').substring(0, this.length);
      this.text = input.value;
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
  background: @color-text;
  border: 1px solid @color-border;
  > span {
    position: absolute;
    font-size: 12px;
    color: @color-background;
    pointer-events: none;
  }
  > input {
    box-sizing: content-box;
    padding-left: 15px;
    font-size: 12px;
    color: @color-background;
  }
  > input::placeholder {
    color: @color-background;
  }
}
</style>
