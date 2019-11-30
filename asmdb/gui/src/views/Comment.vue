<template>
  <input class="comment-container" @input="onInput" @compositionstart="onCompositionStart" @compositionend="onCompositionEnd" @keypress="onKeyPress" @blur="onBlur" />
</template>

<script>
export default {
  props: {
    value: String
  },
  methods: {
    blur: function() {
      //todo
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.comment-container {
  font-size: 12px;
  color: @color-text-dark;
}
</style>
