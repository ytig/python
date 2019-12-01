<template>
  <div class="gird-container">
    <div v-for="i in Math.ceil(items.length/column)" :key="i-1">
      <div v-for="j in column" :key="(i-1)*column+j-1" :style="{width:(100/column)+'%'}">
        <slot v-if="(i-1)*column+j-1<items.length" :item="items[(i-1)*column+j-1]" :index="(i-1)*column+j-1"></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    column: Number,
    items: Array
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.gird-container {
  > div {
    > div {
      display: inline-block;
    }
  }
}
</style>
