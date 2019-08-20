<template>
  <div class="title-container">
    <span class="user-select-none">{{name}}</span>
  </div>
</template>

<script>
export default {
  props: {
    name: String
  }
};
</script>

<style lang="less">
.title-container {
  height: 36px;
  padding: 0px 12px;
  line-height: 36px;
  span {
    font-size: 18px;
    color: @color-title;
    font-family: "Wawati SC";
  }
}
</style>
