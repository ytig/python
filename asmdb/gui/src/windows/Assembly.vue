<template>
  <div>
    <Navigation :name="'Assembly'"></Navigation>
    <Scroller ref="scroller" class="assembly-scroller" #default="props"></Scroller>
  </div>
</template>

<script>
export default {};
</script>

<style lang="less">
@import '~@/styles/theme';
</style>
