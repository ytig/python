<template>
  <div ref="container" v-show="show" class="editor-container" :style="{left:left+'px',top:top+'px',transform:'scale('+scale+','+scale+')'}">
    <span>0x</span>
    <input ref="input" type="text" :style="{width:inputWidth+'px'}" :placeholder="placeholder" @input="onInput" @compositionstart="onCompositionStart" @compositionend="onCompositionEnd" @keypress="onKeyPress" @blur="onBlur" spellcheck="false" />
  </div>
</template>

<script>
import Animation from '@/scripts/animation';

function getChildIndex(parent, child) {
  while (child) {
    if (child.parentNode == parent) {
      return new Array(...parent.childNodes).indexOf(child);
    }
    child = child.parentNode;
  }
  return -1;
}

function correctInput(value, length) {
  while (true) {
    var i = value.indexOf('0x');
    if (i < 0) {
      break;
    }
    value = value.substring(i + 2);
  }
  return value.replace(/[^0-9a-f]/g, '').substring(0, length);
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
      text: '',
      anim: new Animation(1 / 147)
    };
  },
  computed: {
    inputWidth: function() {
      var w1 = measureText(this.text);
      var w2 = measureText(this.placeholder);
      return Math.ceil(1 + Math.max(w1, w2));
    },
    scale: function() {
      var input = this.anim.value;
      var T = 2;
      var output = (T + 1) * Math.pow(input - 1, 3) + T * Math.pow(input - 1, 2) + 1;
      return output;
    }
  },
  methods: {
    alert: function(left, top, length, placeholder, listener) {
      this.close();
      this.left = left - 5;
      this.top = top - 5;
      this.show = true;
      this.length = length;
      this.placeholder = placeholder;
      this.listener = listener;
      this.composition = false;
      this.text = '';
      this.$refs.input.value = '';
      this.$nextTick(() => {
        this.$refs.input.focus();
      });
      this.anim.$value(0);
      this.anim.$target(1);
    },
    close: function() {
      if (this.listener != null) {
        var text = correctInput(this.text, this.length);
        if (text) {
          this.listener(parseInt('0x' + text));
        }
        this.listener = null;
      }
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
      input.value = correctInput(input.value, this.length);
      this.text = input.value;
    },
    onKeyPress: function(event) {
      if (event.keyCode == 13) {
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
  background: #ff0;
  > span {
    position: absolute;
    padding-top: 5px;
    padding-bottom: 3px;
    padding-left: 5px;
    font-size: 12px;
    color: #000;
    pointer-events: none;
  }
  > input {
    box-sizing: content-box;
    padding-top: 5px;
    padding-bottom: 3px;
    padding-left: 20px;
    padding-right: 4px;
    line-height: 14px;
    font-size: 12px;
    color: #000;
  }
}
</style>
