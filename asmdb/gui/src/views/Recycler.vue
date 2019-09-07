<template>
  <div class="recycler-container">
    <div v-for="item in items" :key="item[kk]">
      <slot :item="item"></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    kk: String,
    items: Array
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.recycler-container {
  overflow: scroll;
}
</style>
