<template>
  <div class="navigation2-container">
    <div>
      <div></div>
    </div>
    <span class="navigation2-icon" :style="{backgroundImage:backgroundImage}" :css-focus="focus" @click="onClick"></span>
    <div @click="onClick">
      <div></div>
    </div>
    <span class="navigation2-text user-select-none" :css-focus="focus" @click="onClick">{{name}}</span>
    <div>
      <div></div>
      <slot></slot>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    name: String,
    focus: Boolean
  },
  computed: {
    backgroundImage: function() {
      var icons = {
        python3: 'terminal'
      };
      var url = '/static/icons/' + icons[this.name] + '.png';
      return "url('" + url + "')";
    }
  },
  methods: {
    onClick: function(event) {
      this.$emit('mouseup2', event);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.navigation2-container {
  height: 16px;
  display: flex;
  align-items: center;
  > div {
    position: relative;
    height: 100%;
    > div:first-child {
      position: absolute;
      left: 0px;
      top: 8px;
      width: 100%;
      height: 1px;
      background: @color-border-light;
      pointer-events: none;
    }
  }
  > div:nth-of-type(1) {
    width: 12px;
  }
  > div:nth-of-type(2) {
    width: 8px;
    cursor: se-resize;
  }
  > div:nth-of-type(3) {
    flex-grow: 1;
  }
  > span {
    cursor: se-resize;
  }
  .navigation2-icon {
    width: 16px;
    height: 16px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
  }
  .navigation2-icon[css-focus] {
    filter: brightness(138%);
  }
  .navigation2-text {
    font-size: 14px;
    font-family: 'Wawati SC';
    color: @color-text;
  }
  .navigation2-text[css-focus] {
    color: @color-text-light;
  }
}
</style>
