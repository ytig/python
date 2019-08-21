<template>
  <div class="gird-container">
    <div v-for="i in Math.ceil(items.length/3)" :key="i">
      <div v-for="j in column" :key="i*column+j" :style="{width:(100/column)+'%'}">
        <slot v-if="i*column+j<items.length" :item="items[i*column+j]" :index="i*column+j"></slot>
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
.gird-container {
  > div {
    > div {
      display: inline-block;
    }
  }
}
</style>
