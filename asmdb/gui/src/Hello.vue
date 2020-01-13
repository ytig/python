<template>
  <div class="hello-container" @click="startDebug">
    <canvas id="tween"></canvas>
    <span>Hello World!</span>
  </div>
</template>

<script>
var tweenAlive = false;

function initTween() {
  tweenAlive = true;
  var canvas = document.getElementById('tween');
  var s = devicePixelRatio;
  canvas.style.width = screen.width + 'px';
  canvas.style.height = screen.height + 'px';
  canvas.width = devicePixelRatio * screen.width;
  canvas.height = devicePixelRatio * screen.height;
  requestAnimationFrames(() => {
    if (!initCanvas) {
      return false;
    }
    if (tweenAlive) {
      initCanvas('tween');
    }
    return true;
  });
}

function killTween() {
  kill();
  TweenLite.ticker.sleep();
  C = c = undefined;
  tweenAlive = false;
}

export default {
  mounted: function() {
    initTween();
  },
  destroyed: function() {
    killTween();
  },
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
  position: relative;
  background: @color-background;
  width: 100%;
  height: 100%;
  overflow: hidden;
  > canvas {
    position: absolute;
  }
  > span {
    align-self: center;
    font-size: 16px;
    color: @color-text;
  }
}
</style>
