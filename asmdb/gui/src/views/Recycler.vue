<template>
  <div class="recycler-container" @scroll="onScroll">
    <div v-for="item in items" :key="item.idx">
      <slot :item="item"></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    items: Array
  },
  watch: {
    items: function() {
      console.log('items changed');
    }
  },
  methods: {
    onScroll: function() {
      console.log('scroll');
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.recycler-container {
  overflow: scroll;
}
</style>
