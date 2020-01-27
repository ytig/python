<template>
  <div class="animate-button-container user-select-none" @mouseenter="onMouseEnter" @mousemove="onMouseMove" @mouseleave="onMouseLeave" @click="onClick" @keypress="onKeyPress" tabindex="0">{{text}}</div>
</template>

<script>
import Animation from '@/scripts/animation';

export default {
  data: function() {
    return {
      hover: false,
      focus: false,
      anim: new Animation(1 / 224)
    };
  },
  props: {
    text: String
  },
  watch: {
    hover: function() {
      this.onAnim();
    },
    focus: function() {
      this.onAnim();
    }
  },
  computed: {},
  methods: {
    onMouseEnter: function() {
      this.hover = true;
    },
    onMouseMove: function() {
      this.hover = true;
    },
    onMouseLeave: function() {
      this.hover = false;
    },
    onFocus: function() {
      this.focus = true;
    },
    onBlur: function() {
      this.focus = false;
    },
    onAnim: function() {
      if (this.focus || this.hover) {
        this.anim.$target(1);
      } else {
        this.anim.$target(0);
      }
    },
    onKeyPress: function(event) {
      if (event.keyCode == 13) {
        this.onClick();
      }
    },
    onClick: function() {
      this.$emit('enter');
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.animate-button-container {
  height: 32px;
  line-height: 32px;
  font-size: 12px;
  border-radius: 4px;
  text-align: center;
  color: @color-text-light;
  background-color: @color-background-enter;
  box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.6);
  cursor: pointer;
  outline: none;
}
</style>
