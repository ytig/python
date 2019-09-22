<template>
  <div class="register-container">
    <span class="user-select-none">{{name}}</span>
    <span v-for="i in (fill+1-name.length)" :key="i" class="user-select-none">&nbsp;</span>
    <span v-show="value!=null">{{value}}</span>
  </div>
</template>

<script>
export default {
  props: {
    name: String,
    value: Number,
    fill: Number
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
