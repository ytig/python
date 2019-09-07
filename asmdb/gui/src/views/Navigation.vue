<template>
  <div class="navigation-container" :css-gradient="gradient">
    <span class="user-select-none" :css-focus="focus" :css-disable="disable">{{name}}</span>
    <div v-if="gradient" class="navigation-gradient"></div>
  </div>
</template>

<script>
export default {
  props: {
    name: String,
    focus: Boolean,
    disable: Boolean,
    gradient: Boolean
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.navigation-container {
  position: relative;
  height: 40px;
  > span {
    line-height: 40px;
    padding-left: 12px;
    font-size: 16px;
    color: @color-text;
    font-family: 'Wawati SC';
  }
  > span[css-focus] {
    color: @color-light-text;
  }
  > span[css-disable] {
    text-decoration: line-through;
  }
  .navigation-gradient {
    position: absolute;
    top: 36px;
    width: 100%;
    height: 2px;
    background: linear-gradient(@color-background, transparent);
  }
}
.navigation-container[css-gradient] {
  height: 36px;
}
</style>
