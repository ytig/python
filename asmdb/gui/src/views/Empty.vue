<template>
  <div class="empty-container user-select-none">{{text}}</div>
</template>

<script>
export default {
  props: {
    text: String
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.empty-container {
  padding-left: 24px;
  line-height: 18px;
  font-size: 12px;
  color: @color-text-dark;
  font-style: italic;
}
</style>
