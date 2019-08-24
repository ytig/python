<template>
  <div class="navigation-container">
    <div v-show="focus" class="navigation-focus"></div>
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
  line-height: 36px;
  .navigation-focus {
    position: absolute;
    width: 100%;
    height: 4px;
    background: @color-selection-background;
  }

  > span {
    padding-left: 12px;
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
