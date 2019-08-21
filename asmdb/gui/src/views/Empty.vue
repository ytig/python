<template>
  <div class="empty-container user-select-none">{{value}}</div>
</template>

<script>
export default {
  props: {
    value: String
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.empty-container {
  text-align: center;
  color: @color-dark-text;
  font-size: 12px;
  text-shadow: 1px 1px 2px @color-text-shadow;
}
</style>
