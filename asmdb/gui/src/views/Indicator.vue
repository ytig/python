<template>
  <div class="indicator-container">
    <div
      v-for="(item,index) in Array(size)"
      :key="index"
      :class="'indicator-item'+(item-value)"
    >{{index}}</div>
  </div>
</template>

<script>
export default {
  props: {
    size: {
      type: Number
    },
    value: {
      type: Number
    }
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.indicator-container {
  display: flex;
  > *:first-child {
    border-left: 0px;
  }
  > * {
    flex-grow: 1;
    height: 40px;
    line-height: 40px;
    background: @color-dark-background;
    border-top: 1px solid @color-border;
    border-left: 1px solid @color-border;
    text-align: center;
    color: #abb2bf;
    font-size: 12px;
  }
}
</style>
