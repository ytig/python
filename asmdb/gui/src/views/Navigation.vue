<template>
  <div class="navigation-container">
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
  height: 40px;
  line-height: 40px;
  padding-left: 12px;
  > span {
    font-size: 16px;
    color: @color-text;
    font-family: 'Wawati SC';
  }
  > span[css-focus='true'] {
    color: @color-light-text;
  }
  > span[css-disable='true'] {
    text-decoration: line-through;
  }
}
</style>
