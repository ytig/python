<template>
  <div class="hello-container">
    <div class="hello-grow"></div>
    <div class="hello-title">ASM Debugger</div>
    <div class="hello-input">PL</div>
    <div class="hello-input">PR</div>
    <div class="hello-input">SC</div>
    <div class="hello-button">start debug</div>
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
@font-face {
  font-family: logo;
  src: url('/static/fonts/Quantum.otf');
}

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
  .hello-title {
    margin-bottom: 24px;
    font-size: 24px;
    font-family: logo;
    color: #121212;
  }
  .hello-input {
    margin-bottom: 8px;
    width: 250px;
    font-size: 12px;
    line-height: 32px;
    padding: 0px 12px;

    border-radius: 4px;
    background-color: #121212;

    color: @color-text;
    box-shadow: inset 0 2px 7px 0 rgba(0, 0, 0, 0.8);
  }
  .hello-button {
    margin-top: 16px;
    margin-bottom: 70px;

    width: 250px;
    font-size: 12px;
    line-height: 32px;
    padding: 0px 12px;

    border-radius: 4px;
    background-color: #121212;

    text-align: center;
    color: @color-text-light;

    background-color: #c24038;
    box-shadow: 0 2px 7px 0 rgba(0, 0, 0, 0.6);
  }
}
</style>
