<template>
  <div class="hello-container">
    <div class="hello-grow"></div>
    <div class="hello-title user-select-none">ASM Debugger</div>
    <div class="hello-input" css-theme="0">
      <div></div>
      <input type="text" v-model="device" />
    </div>
    <div class="hello-input" css-theme="1">
      <div></div>
      <input type="text" v-model="process" />
    </div>
    <div class="hello-input" css-theme="2">
      <div></div>
      <input type="text" v-model="script" />
    </div>
    <div class="hello-button user-select-none" :style="{marginBottom:barHeight+'px'}" @click="startDebug">start debug</div>
    <div class="hello-grow"></div>
    <a class="hello-copyright user-select-none" href="https://github.com/ytig" target="_blank">
      <span>power&nbsp;by&nbsp;</span>
      <span>ytig</span>
    </a>
  </div>
</template>

<script>
import resize from '@/scripts/resize';

function getToken(obj, key) {
  var token = obj.get('token');
  if (!token || typeof token != 'object') {
    token = {};
  }
  var val = token[key];
  if (typeof val != 'string') {
    val = '';
  }
  return val;
}

function setToken(obj, key, val) {
  var token = obj.get('token');
  if (!token || typeof token != 'object') {
    token = {};
  }
  token[key] = val;
  obj.set('token', token);
}

function delToken(obj, key) {
  var token = obj.get('token');
  if (!token || typeof token != 'object') {
    token = {};
  }
  delete token[key];
  obj.set('token', token);
}

export default {
  getToken: getToken,
  setToken: setToken,
  delToken: delToken,
  data: function() {
    return {
      device: getToken(this.$cookies, 'device'),
      process: getToken(this.$cookies, 'process'),
      script: getToken(this.$cookies, 'script'),
      barHeight: 0
    };
  },
  mounted: function() {
    resize.registerEvent(this);
    this.onResize();
  },
  destroyed: function() {
    resize.unregisterEvent(this);
  },
  methods: {
    onResize: function() {
      requestAnimationFrames(i => {
        this.barHeight = window.outerHeight - window.innerHeight;
        return !(i < 60);
      });
    },
    startDebug: function() {
      setToken(this.$cookies, 'device', this.device);
      setToken(this.$cookies, 'process', this.process);
      setToken(this.$cookies, 'script', this.script);
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
      text-overflow: ellipsis;
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
    filter: brightness(144%);
  }
  .hello-copyright {
    position: fixed;
    right: 12px;
    bottom: 8px;
    > span {
      cursor: pointer;
    }
    > span:first-child {
      font-size: 12px;
      color: @color-text-dark;
    }
    > span:last-child {
      font-size: 14px;
      color: @color-text4;
    }
  }
}
</style>
