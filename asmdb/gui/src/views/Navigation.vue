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
  > div {
    position: absolute;
    border: 0px solid @color-text;
    border-right-color: transparent !important;
    border-bottom-color: transparent !important;
  }
  > div[css-focus='true'] {
    border-width: 5px;
  }
  > div[css-disable='true'] {
    border-color: @color-darker-text;
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
