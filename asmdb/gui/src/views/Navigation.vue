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
    width: 100%;
    height: 2px;
  }
  > div[css-focus='true'] {
    background: @color-text;
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
