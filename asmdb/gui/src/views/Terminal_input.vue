<template>
  <div class="terminal-input-container">
    <input ref="input" class="terminal-input-input" type="text" :style="{width:inputWidth+'px'}" @input="onInput" @compositionstart="onCompositionStart" @compositionend="onCompositionEnd" @blur="onBlur" />
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      composition: false,
      text: ''
    };
  },
  props: {
    focus: Boolean
  },
  watch: {
    focus: {
      immediate: true,
      handler: function callee(newValue, oldValue) {
        if (this.$el == undefined) {
          this.$nextTick(callee.bind(this, ...arguments));
          return;
        }
        var input = this.$refs.input;
        if (newValue) {
          input.focus();
        } else {
          input.blur();
        }
      }
    }
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
      if (!this.composition) {
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
      }
      return null;
    },
    onInput: function() {
      if (!this.composition) {
        this.onCompositionEnd();
      }
    },
    onCompositionStart: function() {
      this.composition = true;
    },
    onCompositionEnd: function() {
      this.composition = false;
      var input = this.$refs.input;
      this.$emit('input', input.value);
      input.value = '';
    },
    onBlur: function() {
      if (this.focus) {
        //todo requestAnimationFrames
        //todo !pressed && !selection
        this.$refs.input.focus();
      }
    },
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
  bottom: 0px;
  background: #fff;
  .terminal-input-input {
    padding: 0px 12px;
    font-size: 12px;
  }
}
</style>
