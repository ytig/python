<template>
  <div class="stack-container">
    <Title :name="'Stack'"></Title>
    <div v-for="i in Array(40)" :key="i">
      <div class="todo">1234 00 01 02 03 04 05 06 07 &nbsp;08 09 0a 0b 0c 0d 0e 0f</div>
    </div>
  </div>
</template>

<script>
export default {};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.stack-container {
  .todo {
    padding: 0px 12px;
    color: #abb2bf;
    font-size: 12px;
  }
}
</style>
