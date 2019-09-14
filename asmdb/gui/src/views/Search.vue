<template>
  <div class="search-container">
    <input type="text" />
  </div>
</template>

<script>
export default {};
</script>

<style lang="less">
@import '~@/styles/theme';

.search-container {
  position: fixed;
  > input {
    font-size: 12px;
  }
}
</style>
