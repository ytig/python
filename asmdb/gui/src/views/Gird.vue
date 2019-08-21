<template>
  <div class="gird-container">
    <div v-for="(item, index) in value" :key="item.id">
      <slot :item="item" :index="index"></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    value: Array
  }
};
</script>

<style lang="less">
.gird-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
}
</style>
