<template>
  <div class="memory-container">
    <Title :name="'Memory'"></Title>
    <span class="todo">0xbf001234 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f ........aaaaaaaa</span>
  </div>
</template>

<script>
export default {};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.memory-container {
  .todo {
    color: #abb2bf;
    font-size: 14px;
  }
}
</style>
