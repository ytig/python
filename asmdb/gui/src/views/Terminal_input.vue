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
