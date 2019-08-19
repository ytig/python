<template>
  <div class="title-container">
    <span>{{name}}</span>
  </div>
</template>

<script>
export default {
  name: "Title",
  props: {
    name: String
  }
};
</script>

<style lang="less" scoped>
@import "~@/styles/global.less";

.title-container {
  padding: 0px 12px;
  line-height: 36px;
  span {
    font-size: 18px;
    color: @color-title;
  }
}
</style>
