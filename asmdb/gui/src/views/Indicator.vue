<template>
  <div class="indicator-container">
    <div
      v-for="(item,index) in Array(size)"
      :key="index"
      :class="'user-select-none indicator-item'+(index-value)+(disable?' indicator-disable':'')"
      :style="{flexGrow:1/(2+index)}"
      @click="onClickItem(index)"
    >{{index}}</div>
  </div>
</template>

<script>
export default {
  props: {
    size: Number,
    value: Number,
    disable: Boolean
  },
  methods: {
    onClickItem: function(index) {
      if (this.value == index) {
        return;
      }
      if (this.disable) {
        return;
      }
      this.value = index;
      this.$emit("input", this.value);
    }
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.indicator-container {
  display: flex;
  > * {
    height: 40px;
    line-height: 40px;
    text-align: center;
    font-size: 12px;
    border-top: 1px solid @color-light-border;
    color: @color-dark-content;
    cursor: pointer;
  }
  .indicator-item0 {
    color: @color-light-content;
    text-decoration: underline;
    cursor: default;
  }
  .indicator-disable {
    color: @color-dark-content !important;
    cursor: not-allowed !important;
  }
}
</style>
