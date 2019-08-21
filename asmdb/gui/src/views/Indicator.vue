<template>
  <div class="indicator-container">
    <div v-for="i in size" :key="i" :class="'user-select-none indicator-item'+(i-1-value)+(disable?' indicator-disable':'')" :style="{flexGrow:1/(i+1)}" @click="onClickItem(i-1)">{{i-1}}</div>
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
      this.$emit("input", index);
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
    color: @color-dark-text;
    cursor: pointer;
  }
  .indicator-item0 {
    color: @color-light-text;
    text-decoration: underline;
    cursor: default;
  }
  .indicator-disable {
    color: @color-dark-text !important;
    text-decoration: none !important;
    cursor: not-allowed !important;
  }
}
</style>
