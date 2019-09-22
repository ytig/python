<template>
  <div class="register-container">
    <span class="user-select-none">{{value.lineName}}</span>
    <span v-for="i in (value.lineFill+1-value.lineName.length)" :key="i" class="user-select-none">&nbsp;</span>
    <span v-show="value.newValue!=null">{{value.newValue}}</span>
  </div>
</template>

<script>
export default {
  props: {
    value: Object
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.register-container {
  padding-left: 12px;
  padding-right: 12px;
  padding-bottom: 4px;
  > span {
    font-size: 12px;
    color: @color-text;
  }
}
</style>
