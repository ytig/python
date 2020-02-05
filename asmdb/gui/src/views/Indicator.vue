<template>
  <div class="indicator-container">
    <div v-for="i in size" :key="i" class="user-select-none" :style="{flexGrow:1/(i+1)}" @click="onClickItem(i-1)" :css-offset="i-1-value" :css-disable="disable">{{i-1}}</div>
  </div>
</template>

<script>
export default {
  props: {
    size: Number,
    value: Number,
    disable: Boolean
  },
  watch: {
    value: function() {
      emptySelection();
    }
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
@import '~@/styles/theme';

.indicator-container {
  display: flex;
  > * {
    height: 36px;
    padding-top: 8px;
    text-align: center;
    font-size: 12px;
    border-top: 1px solid @color-border-light;
    color: @color-text-dark;
    cursor: pointer;
  }
  > *[css-offset='0'] {
    color: @color-text-light;
    text-decoration: underline;
    cursor: default;
  }
  > *[css-disable] {
    color: @color-text-dark !important;
    text-decoration: none !important;
    cursor: not-allowed !important;
  }
}
</style>
