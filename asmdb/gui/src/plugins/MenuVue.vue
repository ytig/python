<template>
  <div class="menu-container">
    <div>1</div>
    <div>2</div>
  </div>
</template>

<script>
export default {
  props: {
    show: Boolean,
    items: Array
  },
  methods: {}
};
</script>

<style lang="less">
@import '~@/styles/theme';

.menu-container {
  position: fixed;
  width: 100%;
  height: 100%;
}
</style>
