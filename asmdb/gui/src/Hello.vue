<template>
  <div class="hello-container">
    <div class="hello-grow"></div>
    <div class="hello-content">
      <div>PL</div>
      <div>PR</div>
      <div>SC</div>
      <div>start debug</div>
    </div>
    <div class="hello-grow"></div>
  </div>
</template>

<script>
export default {
  methods: {
    startDebug: function() {
      document.body.webkitRequestFullScreen();
      this.$router.replace('/world');
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.hello-container {
  background: @color-background;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  .hello-grow {
    flex-grow: 1;
  }
  .hello-content {
    div {
      margin: 8px 0px;
      width: 250px;
      font-size: 12px;
      line-height: 32px;
      padding: 0px 12px;

      border-radius: 4px;
      background-color: #121212;

      color: @color-text;
      box-shadow: inset 0 2px 7px 0 rgba(0, 0, 0, 0.8);
    }
    div:last-child {
      text-align: center;
      color: @color-text-light;
      margin-top: 24px;
      background-color: #c24038;
      box-shadow: 0 2px 7px 0 rgba(0, 0, 0, 0.6);
    }
  }
}
</style>
