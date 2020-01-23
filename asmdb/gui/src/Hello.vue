<template>
  <div class="hello-container">
    <div class="hello-grow"></div>
    <div class="hello-title user-select-none">ASM Debugger</div>
    <div class="hello-input" css-theme="0">
      <div></div>
      <input type="text" />
    </div>
    <div class="hello-input" css-theme="1">
      <div></div>
      <input type="text" />
    </div>
    <div class="hello-input" css-theme="2">
      <div></div>
      <input type="text" />
    </div>
    <div class="hello-button user-select-none" @click="startDebug">start debug</div>
    <div class="hello-grow"></div>
    <div class="hello-copyright">
      <a class="user-select-none" href="https://github.com/ytig" target="_blank">power by YTIG</a>
    </div>
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
  font-family: 'logo font';
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
    font-family: 'logo font';
    color: @color-background-darker;
  }
  .hello-input {
    position: relative;
    margin-bottom: 8px;
    width: 294px;
    height: 32px;
    border-radius: 4px;
    background-color: @color-background-darker;
    box-shadow: inset 0px 2px 7px rgba(0, 0, 0, 0.8);
    > div:first-child {
      position: absolute;
      left: 12px;
      top: 8px;
      width: 16px;
      height: 16px;
      background-size: 16px 16px;
      background-repeat: no-repeat;
      background-position: center center;
      pointer-events: none;
    }
    > input {
      width: 100%;
      padding-left: 36px;
      padding-right: 12px;
      line-height: 32px;
      font-size: 12px;
      color: @color-text;
    }
  }
  .hello-input[css-theme='0'] {
    > div:first-child {
      background-image: url('/static/icons/device.png');
    }
  }
  .hello-input[css-theme='1'] {
    > div:first-child {
      background-image: url('/static/icons/process.png');
    }
  }
  .hello-input[css-theme='2'] {
    > div:first-child {
      background-image: url('/static/icons/script.png');
    }
  }
  .hello-button {
    margin-top: 16px;
    margin-left: 182px;
    width: 112px;
    height: 32px;
    line-height: 32px;
    font-size: 12px;
    border-radius: 4px;
    text-align: center;
    color: @color-text-light;
    background-color: @color-background-enter;
    box-shadow: 0px 2px 7px rgba(0, 0, 0, 0.6);
    cursor: pointer;
  }
  .hello-button:hover {
    filter: brightness(128%);
  }
  .hello-copyright {
    width: 100%;
    height: 111px;
    padding-right: 12px;
    padding-bottom: 8px;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    align-items: flex-end;
    > a {
      font-size: 16px;
      font-family: 'logo font';
      color: @color-background-darker;
      cursor: pointer;
      text-decoration: none;
    }
  }
}
</style>
