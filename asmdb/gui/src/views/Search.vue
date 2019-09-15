<template>
  <div v-show="showing" class="search-container">
    <input ref="input" type="text" v-model="text" @keypress="onKeyPress" @blur="onBlur" />
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      showing: false,
      intercept: false,
      text: ''
    };
  },
  created: function() {
    document.addEventListener('mousedown', this.onDomMouseDown, true);
    document.addEventListener('click', this.onDomClick, true);
    document.addEventListener('keydown', this.onDomKeyDown, true);
  },
  destroyed: function() {
    document.removeEventListener('mousedown', this.onDomMouseDown, true);
    document.removeEventListener('click', this.onDomClick, true);
    document.removeEventListener('keydown', this.onDomKeyDown, true);
  },
  updated: function() {
    var input = this.$refs.input;
    if (this.showing) {
      input.focus();
    }
  },
  methods: {
    show: function() {
      this.showing = true;
      this.text = '';
    },
    dismiss: function() {
      this.showing = false;
    },
    onKeyPress: function(event) {
      if (event.keyCode == 13) {
        this.$emit('search', this.text);
        this.dismiss();
      }
    },
    onBlur: function() {
      this.dismiss();
    },
    onDomMouseDown: function(event) {
      this.intercept = this.showing;
    },
    onDomClick: function(event) {
      if (this.intercept) {
        event.stopPropagation();
      }
    },
    onDomKeyDown: function(event) {
      if (this.showing) {
        event.stopPropagation();
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.search-container {
  position: absolute;
  z-index: 1;
  left: 4px;
  top: 4px;
  > input {
    font-size: 12px;
  }
}
</style>
