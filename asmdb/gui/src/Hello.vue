<template>
  <div class="hello-container" @click="startDebug">
    <span>Hello World!</span>
  </div>
</template>

<script>
export default {
  methods: {
    startDebug: function() {
      this.$router.replace('/world');
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.hello-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  > span {
    align-self: center;
    font-size: 16px;
  }
}
</style>
