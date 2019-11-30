<template>
  <input ref="input" class="comment-input" type="text" :style="{width:inputWidth+'px'}" @input="onInput" @keypress="onKeyPress" @blur="onBlur" />
</template>

<script>
import InputMixin from './InputMixin';

export default {
  mixins: [InputMixin],
  data: function() {
    return {
      text: ''
    };
  },
  props: {
    value: String
  },
  watch: {
    value: function(newValue, oldValue) {
      this.text = newValue;
      this.$refs.input.value = this.text;
    }
  },
  computed: {
    inputWidth: function() {
      var w = measureText(this.text);
      return 2 + 6 + Math.ceil(1 + w);
    }
  },
  mounted: function() {
    this.text = this.value;
    this.$refs.input.value = this.text;
  },
  methods: {
    onShow: function() {
      this.$refs.input.focus();
    },
    onDismiss: function() {
      this.$refs.input.blur();
      this.$emit('input', this.text);
    },
    onInput: function() {
      this.text = this.$refs.input.value;
    },
    onKeyPress: function(event) {
      if (event.keyCode == 13) {
        this.dismiss();
      }
    },
    onBlur: function() {
      this.dismiss();
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.comment-input {
  padding-right: 6px;
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
</style>
