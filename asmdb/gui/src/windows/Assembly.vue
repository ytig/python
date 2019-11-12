<template>
  <div class="assembly-container">
    <Navigation :name="'Assembly'"></Navigation>
    <Scroller ref="scroller" class="assembly-scroller" #default="props"></Scroller>
  </div>
</template>

<script>
export default {};
</script>

<style lang="less">
@import '~@/styles/theme';

.assembly-container {
  position: relative;
  display: flex;
  flex-direction: column;
  .assembly-scroller {
    width: 147px;
    height: 0px;
    flex-grow: 1;
  }
}
</style>
