<template>
  <div class="memory-container">
    <Title :name="'Memory'"></Title>
    <div v-for="i in Array(40)" :key="i">
      <span class="todo">bf001234 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f ........aaaaaaaa</span>
    </div>
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
    font-size: 12px;
  }
}
</style>
