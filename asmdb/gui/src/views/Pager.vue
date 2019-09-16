<template>
  <div class="pager-container"></div>
</template>

<script>
export default {
  props: {
    canSub: Boolean,
    canAdd: Boolean
  },
  methods: {}
};
</script>

<style lang="less">
@import '~@/styles/theme';

.pager-container {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
