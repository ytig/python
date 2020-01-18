<template>
  <div class="hello-container">
    <canvas id="tween"></canvas>
    <span>Hello World!</span>
  </div>
</template>

<script>
var tweenAlive = false;

function initTween() {
  tweenAlive = true;
  var width = screen.width;
  var height = screen.height;
  var canvas = document.getElementById('tween');
  canvas.style.width = width + 'px';
  canvas.style.height = height + 'px';
  canvas.width = devicePixelRatio * width;
  canvas.height = devicePixelRatio * height;
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
