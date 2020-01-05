<template>
  <div class="terminal-input-container">
    <input ref="input" class="terminal-input-input" type="text" :style="{width:inputWidth+'px'}" @input="onInput" @compositionstart="onCompositionStart" @compositionend="onCompositionEnd" @keypress="onKeyPress" @blur="onBlur" />
  </div>
</template>

<script>
export default {
  props: {
    focus: Boolean
  },
  computed: {
    inputWidth: function() {
      //todo
      return 100;
    }
  },
  created: function() {
    window.addEventListener('keydown', this.onDomKeyDown, true);
  },
  destroyed: function() {
    window.removeEventListener('keydown', this.onDomKeyDown, true);
  },
  methods: {
    preInput: function(event) {
      switch (event.key) {
        case 'Enter':
          return '\n';
        case 'Backspace':
          return '\x08';
        case 'Tab':
          return '\x09';
        case 'ArrowLeft':
          return '\x02';
        case 'ArrowRight':
          return '\x06';
        case 'ArrowUp':
          return '\x10';
        case 'ArrowDown':
          return '\x0e';
      }
      return null;
    },
    onInput: function() {
      if (this.focus) {
        this.$emit('input', this.$refs.input.value);
        this.$refs.input.value = '';
      }
    },
    onCompositionStart: function() {},
    onCompositionEnd: function() {},
    onKeyPress: function(event) {},
    onBlur: function() {},
    onDomKeyDown: function(event) {
      if (this.focus) {
        event.stopPropagation();
        var utf8 = this.preInput(event);
        if (utf8 != null) {
          event.preventDefault();
          if (utf8) {
            this.$emit('input', utf8);
          }
        }
        //todo clear selection
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.terminal-input-container {
  position: absolute;
  left: 0px;
  top: 0px;
  background: #fff;
  .terminal-input-input {
    font-size: 12px;
  }
}
</style>
