<template>
  <div class="animate-button-container user-select-none" @focus="onFocus" @blur="onBlur" @mouseenter="onMouseEnter" @mousemove="onMouseMove" @mouseleave="onMouseLeave" @click="onClick" @keypress="onKeyPress" tabindex="0">
    <div :style="{opacity:alpha1,transform:'scale('+scale1+','+scale1+')'}"></div>
    <div :style="{opacity:alpha2,transform:'scale('+scale2+','+scale2+')'}"></div>
    <div :style="{opacity:alpha3}">{{text}}</div>
    <div :style="{opacity:alpha4}">{{text}}</div>
  </div>
</template>

<script>
import Animation from '@/scripts/animation';

export default {
  data: function() {
    return {
      hover: false,
      focus: false,
      anim: new Animation(1 / 128)
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
  computed: {
    alpha1: function() {
      return 1 - this.anim.value;
    },
    scale1: function() {
      return 1 * (1 - this.anim.value) + 0.8 * this.anim.value;
    },
    alpha2: function() {
      return this.anim.value;
    },
    scale2: function() {
      return 1.2 * (1 - this.anim.value) + 1 * this.anim.value;
    },
    alpha3: function() {
      return 1 - this.anim.value;
    },
    alpha4: function() {
      return this.anim.value;
    }
  },
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
  position: relative;
  height: 32px;
  outline: none;
  cursor: pointer;
  > div {
    position: absolute;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }
  > div:nth-of-type(1) {
    border-radius: 4px;
    background-color: @color-background-enter;
    box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.6);
  }
  > div:nth-of-type(2) {
    border-radius: 4px;
    border: 2px solid @color-background-enter;
  }
  > div:nth-of-type(3) {
    line-height: 32px;
    font-size: 12px;
    color: @color-text-light;
    text-align: center;
  }
  > div:nth-of-type(4) {
    line-height: 32px;
    font-size: 12px;
    color: @color-background-enter;
    text-align: center;
  }
}
</style>
