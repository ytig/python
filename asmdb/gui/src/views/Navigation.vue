<template>
  <div class="navigation-container">
    <span :class="'user-select-none'+(disable?' navigation-disable':'')">{{name}}</span>
  </div>
</template>

<script>
export default {
  props: {
    name: String,
    disable: Boolean
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.navigation-container {
  height: 36px;
  padding: 0px 12px;
  line-height: 36px;
  > span {
    font-size: 18px;
    color: @color-text;
    font-family: "Wawati SC";
  }
  > span.navigation-disable {
    text-decoration: line-through;
  }
}
</style>
