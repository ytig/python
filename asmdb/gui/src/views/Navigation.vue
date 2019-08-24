<template>
  <div class="navigation-container" :css-focus="focus">
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
  height: 30px;
  padding: 0px 12px;
  display: flex;
  align-items: flex-end;
  > span {
    font-size: 18px;
    color: @color-text;
    font-family: 'Wawati SC';
  }
  > span[css-disable='true'] {
    color: @color-darker-text;
    text-decoration: line-through;
  }
}
.navigation-container[css-focus='true'] {
  background: #67769620;
}
</style>
