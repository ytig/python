<template>
  <div class="gird-container">
    <!-- <div v-for="(key, val) in value" :key="val.id" :style="{'width':width+'px'}">
      <slot :key="key" :val="key"></slot>
    </div>-->
  </div>
</template>

<script>
export default {
  props: {
    width: {
      type: Number
    },
    value: {
      type: Array
    }
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
