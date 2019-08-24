<template>
  <div class="navigation-container">
    <div :css-focus="focus" :css-disable="disable"></div>
    <span class="user-select-none" :css-focus="focus" :css-disable="disable">{{name}}</span>
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
  height: 40px;
  overflow: hidden;
  > div {
    position: absolute;
    width: 14px;
    height: 14px;
    left: -7px;
    top: -7px;
    transform: rotate(45deg);
    background: @color-text;
    opacity: 0;
  }
  > div[css-focus='true'] {
    opacity: 1;
  }
  > div[css-disable='true'] {
    background: @color-darker-text;
  }
  > span {
    position: absolute;
    left: 12px;
    bottom: 5px;
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
