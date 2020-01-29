<template>
  <div ref="container" class="comment-container">
    <input ref="input" class="comment-input" type="text" :style="{width:inputWidth+'px'}" @input="onInput" @keypress="onKeyPress" @focus="show" @blur="dismiss" spellcheck="false" />
  </div>
</template>

<script>
import InputMixin from './InputMixin';

export default {
  mixins: [InputMixin],
  data: function() {
    return {
      maxWidth: 0,
      text: ''
    };
  },
  props: {
    value: String
  },
  watch: {
    value: {
      immediate: true,
      handler: function callee(newValue, oldValue) {
        if (this.$el == undefined) {
          this.$nextTick(callee.bind(this, ...arguments));
          return;
        }
        this.text = newValue;
        this.$refs.input.value = newValue;
      }
    }
  },
  computed: {
    inputWidth: function() {
      var w = measureText(this.text);
      return Math.min(2 + 4 + Math.ceil(1 + w), this.maxWidth);
    }
  },
  mounted: function() {
    this.maxWidth = this.$refs.container.clientWidth;
  },
  methods: {
    selectEnd: function() {
      var input = this.$refs.input;
      input.selectionStart = input.selectionEnd = input.value.length;
      input.scrollLeft = input.scrollWidth - input.clientWidth;
    },
    onShow: function() {
      this.$refs.input.focus();
    },
    onDismiss: function() {
      this.$refs.input.blur();
      if (this.text != this.value) {
        this.$emit('input', this.text);
      }
    },
    onIntercept: function() {
      return false;
    },
    onInput: function() {
      this.text = this.$refs.input.value;
    },
    onKeyPress: function(event) {
      if (event.keyCode == 13) {
        this.dismiss();
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.comment-container {
  .comment-input {
    padding-right: 4px;
    line-height: 14px;
    font-size: 12px;
    color: @color-text-dark;
    border: 1px solid transparent;
    cursor: pointer;
  }
  .comment-input:hover {
    border: 1px solid @color-text-dark;
  }
  .comment-input:focus {
    border: 1px solid @color-text-dark;
    cursor: default;
  }
}
</style>
