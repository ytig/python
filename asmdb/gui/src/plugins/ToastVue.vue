<template>
  <div v-show="anim.value!=0" class="toast-container">
    <span :style="{opacity:opacity,transform:transform}">{{text}}</span>
  </div>
</template>

<script>
import Animation from '@/scripts/animation';

export default {
  data: function() {
    return {
      text: '',
      counter: 0,
      anim: new Animation(Animation.ease_out(147))
    };
  },
  computed: {
    opacity: function() {
      return this.anim.value;
    },
    transform: function() {
      return 'translateY(' + (1 - this.anim.value) * 50 + '%)';
    }
  },
  methods: {
    alert: function(text, long) {
      var time = !long ? 2000 : 3500;
      this.anim.$target(1);
      this.text = text;
      var counter = ++this.counter;
      setTimeout(() => {
        if (counter != this.counter) {
          return;
        }
        this.close();
      }, time + 147);
    },
    close: function() {
      this.anim.$target(0);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.toast-container {
  position: fixed;
  z-index: 7;
  left: 0px;
  right: 0px;
  bottom: 0px;
  width: 38%;
  height: 38%;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
  pointer-events: none;
  > span {
    padding: 8px 12px;
    border-radius: 4px;
    background: @color-background-darker;
    box-shadow: 0px 2px 4px @color-border-shadow;
    color: @color-text-menu;
    font-size: 12px;
    word-break: break-word;
  }
}
</style>
