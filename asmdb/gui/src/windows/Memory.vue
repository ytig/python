<template>
  <div class="memory-container">
    <Navigation :name="'Memory'" :disable="true"></Navigation>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      disable: true
    };
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.memory-container {
  width: 580px; //todo
}
</style>
