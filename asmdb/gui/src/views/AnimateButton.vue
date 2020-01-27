<template>
  <div class="animate-button-container user-select-none" @focus="onFocus" @blur="onBlur" @mouseenter="onMouseEnter" @mousemove="onMouseMove" @mouseleave="onMouseLeave" @click="onClick" @keypress="onKeyPress" tabindex="0">
    <div>
      <div>{{text}}</div>
    </div>
    <div>
      <div :style="{right:(16-radius)+'px',bottom:(16-radius)+'px',width:(2*radius)+'px',height:(2*radius)+'px'}"></div>
      <div :style="{right:(16-radius)+'px',width:(2*radius)+'px'}">
        <div :style="{left:left+'px'}">{{text}}</div>
      </div>
    </div>
  </div>
</template>

<script>
import Animation from '@/scripts/animation';

export default {
  data: function() {
    return {
      hover: false,
      focus: false,
      width: 0,
      anim: new Animation(1 / 147)
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
    radius: function() {
      return parseInt((this.width / 2) * this.anim.value);
    },
    left: function() {
      return 16 - this.width / 2;
    }
  },
  mounted: function() {
    this.width = this.$el.clientWidth;
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
    left: 0px;
    top: 0px;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }
  > div:first-child {
    border-radius: 4px;
    background-color: @color-background-enter;
    box-shadow: 0px 2px 6px @color-text-shadow;
    display: flex;
    justify-content: center;
    > div {
      line-height: 32px;
      font-size: 12px;
      color: @color-text-light;
    }
  }
  > div:last-child {
    overflow: hidden;
    > div:first-child {
      position: absolute;
      border-radius: 999px;
      background-color: @color-background;
    }
    > div:last-child {
      position: absolute;
      top: 0px;
      height: 100%;
      overflow: hidden;
      display: flex;
      justify-content: center;
      > div {
        position: relative;
        line-height: 32px;
        font-size: 12px;
        color: @color-background-enter;
        white-space: nowrap;
      }
    }
  }
}
</style>
