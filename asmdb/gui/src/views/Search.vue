<template>
  <div v-show="showing" class="search-container" :css-illegal="illegal">
    <div></div>
    <input ref="input" type="text" :style="{width:inputWidth+'px'}" v-model="text" @input="onInput" @keypress="onKeyPress" @blur="onBlur" />
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      showing: false,
      intercept: false,
      text: '',
      realText: ''
    };
  },
  computed: {
    illegal: function() {
      return this.text.length > 5;
    },
    inputWidth: function() {
      return 1 + measureText(this.realText, '12px Menlo');
    }
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
      this.realText = '';
    },
    dismiss: function() {
      this.showing = false;
    },
    onInput: function() {
      this.realText = this.$refs.input.value;
    },
    onKeyPress: function(event) {
      if (event.keyCode == 13) {
        if (this.illegal) {
          console.log('todo anim');
        } else {
          if (this.text) {
            this.$emit('search', this.text);
          }
          this.dismiss();
        }
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
  background: @color-background-popup;
  border-radius: 2px;
  box-shadow: 1px 1px @color-border-shadow;
  > div {
    position: absolute;
    z-index: -1;
    left: 2px;
    top: 3px;
    width: 16px;
    height: 16px;
    background: url('~@/icons/search.png') no-repeat;
  }
  > input {
    box-sizing: content-box;
    border-radius: 2px;
    border: 1px solid transparent;
    padding: 3px 2px 1px 20px;
    font-size: 12px;
    color: @color-text-menu;
  }
}
.search-container[css-illegal] {
  > input {
    border: 1px solid @color-border-illegal;
  }
}
</style>
