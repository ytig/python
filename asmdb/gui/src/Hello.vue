<template>
  <div class="hello-container">
    <div class="hello-grow"></div>
    <div class="hello-title">ASM Debugger</div>
    <div class="hello-input">PL</div>
    <div class="hello-input">PR</div>
    <div class="hello-input">SC</div>
    <div class="hello-button">start debug</div>
    <div class="hello-grow"></div>
    <div class="hello-copyright"></div>
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
    height: 24px;
    font-size: 24px;
    font-family: logo;
    color: #121212;
  }
  .hello-input {
    margin-bottom: 8px;
    width: 294px;
    font-size: 12px;
    line-height: 32px;
    border-radius: 4px;
    padding: 0px 12px;
    color: @color-text;
    background-color: #121212;
    box-shadow: inset 0px 2px 7px 0 rgba(0, 0, 0, 0.8);
  }
  .hello-button {
    margin-top: 16px;
    margin-left: 182px;
    width: 112px;
    font-size: 12px;
    line-height: 32px;
    border-radius: 4px;
    text-align: center;
    color: @color-text-light;
    background-color: #c24038;
    box-shadow: 0px 2px 7px 0 rgba(0, 0, 0, 0.6);
    cursor: pointer;
  }
  .hello-button:hover {
    filter: brightness(128%);
  }
  .hello-copyright {
    height: 111px;
  }
}
</style>
