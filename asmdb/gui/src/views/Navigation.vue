<template>
  <div class="navigation-container">
    <div :css-focus="focus"></div>
    <span class="user-select-none" :css-disable="''+disable">{{name}}</span>
  </div>
</template>

<script>
export default {
  props: {
    name: String,
    focus: Boolean,
    disable: Boolean
  }
};
</script>

<style lang="less">
@import '~@/styles/theme.less';

.navigation-container {
  position: relative;
  height: 36px;
  > div {
    height: 2px;
  }
  > div[css-focus='true'] {
    background: @color-text;
  }
  > span {
    position: absolute;
    top: 6px;
    left: 12px;
    font-size: 18px;
    color: @color-text;
    font-family: 'Wawati SC';
  }
  > span[css-disable='true'] {
    color: @color-darker-text;
    text-decoration: line-through;
  }
}
</style>
