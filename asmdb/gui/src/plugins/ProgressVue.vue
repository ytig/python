<template>
  <div ref="container" v-show="anim.value!=0" class="progress-container" :style="{background:background}">
    <pre class="progress-content" :style="{opacity:opacity}">{{message}}</pre>
  </div>
</template>

<script>
import Animation from '@/scripts/animation';

export default {
  data: function() {
    return {
      message: '',
      anim: new Animation(Animation.ease_out(224))
    };
  },
  computed: {
    background: function() {
      return 'rgba(0, 0, 0, ' + this.anim.value * 0.5 + ')';
    },
    opacity: function() {
      return this.anim.value;
    }
  },
  methods: {
    alert: function() {
      this.anim.$target(1);
      this.message = '';
    },
    progress: function(message) {
      this.message = message;
    },
    close: function() {
      this.anim.$target(0);
    },
    onKeyDown: function(event) {
      var show = this.anim.value != this.anim.target || this.anim.value != 0;
      return show;
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.progress-container {
  position: fixed;
  z-index: 7;
  left: 0px;
  top: 0px;
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: wait;
  .progress-content {
    padding: 12px;
    font-size: 12px;
    color: @color-text-dark;
    cursor: wait;
  }
}
</style>
