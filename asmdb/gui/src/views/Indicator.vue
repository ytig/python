<template>
  <div class="indicator-container">
    <div
      v-for="(item,index) in Array(size)"
      :key="index"
      :class="'user-select-none indicator-item'+(index-value)"
      @click="onClickItem(index)"
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
  },
  methods: {
    onClickItem: function(index) {
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
    flex-grow: 1;
    height: 40px;
    line-height: 40px;
    text-align: center;
    font-size: 12px;
    background: @color-dark-background;
    border-top: 1px solid @color-border;
    border-right: 1px solid @color-border;
    color: @color-dark-content;
    cursor: pointer;
  }
  > *:last-child {
    border-right: 0px;
  }
  > *:hover {
    background: @color-light-background;
  }
  > .indicator-item0 {
    background: transparent;
    border-top: 0px;
    border-right: 0px;
    color: @color-light-content;
    text-decoration: underline;
    line-height: 42px;
    cursor: default;
  }
  > .indicator-item1 {
    border-left: 1px solid @color-border;
    border-radius: 4px 0px 0px 0px;
  }
  > .indicator-item-1 {
    border-radius: 0px 4px 0px 0px;
  }
}
</style>
