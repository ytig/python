<template>
  <div class="indicator-container">
    <div v-for="i in size" :key="i" class="user-select-none" :style="{flexGrow:1/(i+1)}" @click="onClickItem(i-1)" :css-offset="''+(i-1-value)" :css-disable="''+disable">{{i-1}}</div>
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
      this.$emit('input', index);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme.less';

.indicator-container {
  display: flex;
  > * {
    height: 36px;
    padding-top: 8px;
    text-align: center;
    font-size: 12px;
    border-top: 1px solid @color-light-border;
    color: @color-dark-text;
    cursor: pointer;
  }
  > *[css-offset='0'] {
    color: @color-light-text;
    text-decoration: underline;
    cursor: default;
  }
  > *[css-disable='true'] {
    color: @color-dark-text !important;
    text-decoration: none !important;
    cursor: not-allowed !important;
  }
}
</style>
