<template>
  <div class="terminal-input-container">
    <input ref="input" class="terminal-input-input" type="text" :style="{width:inputWidth+'px'}" @input="onInput" @compositionstart="onCompositionStart" @compositionend="onCompositionEnd" @blur="onBlur" />
  </div>
</template>

<script>
const MouseMixin = {
  data: function() {
    return {
      touchingLeft: false,
      touchingRight: false
    };
  },
  created: function() {
    window.addEventListener('mousedown', this.onDomMouseDown, true);
    window.addEventListener('mouseup', this.onDomMouseUp, true);
  },
  destroyed: function() {
    window.removeEventListener('mousedown', this.onDomMouseDown, true);
    window.removeEventListener('mouseup', this.onDomMouseUp, true);
  },
  methods: {
    onDomMouseDown: function(event) {
      if (event.button == 0) {
        this.touchingLeft = true;
      }
      if (event.button == 2) {
        this.touchingRight = true;
      }
    },
    onDomMouseUp: function(event) {
      if (event.button == 0) {
        this.touchingLeft = false;
      }
      if (event.button == 2) {
        this.touchingRight = false;
      }
    }
  }
};

export default {
  mixins: [MouseMixin],
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
        requestAnimationFrames(i => {
          if (!this.focus) {
            return true;
          }
          var autoFocus = !this.touchingLeft && !this.touchingRight && getSelection().type != 'Range' && !this.$menu.show;
          if (autoFocus) {
            this.$refs.input.focus();
          }
          return autoFocus;
        });
      }
    },
    onDomKeyDown: function(event) {
      var focus = document.activeElement == this.$refs.input;
      if (focus) {
        event.stopPropagation();
        var utf8 = this.preInput(event);
        if (utf8 != null) {
          event.preventDefault();
          if (utf8) {
            this.$emit('input', utf8);
          }
        }
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
  pointer-events: none;
  .terminal-input-input {
    padding: 0px 12px;
    font-size: 12px;
  }
}
</style>
