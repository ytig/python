<template>
  <div class="navigationpy-container">
    <div>
      <div></div>
    </div>
    <span class="navigationpy-icon" :css-focus="focus" @click="onClick"></span>
    <div>
      <div @click="onClick"></div>
    </div>
    <span class="navigationpy-text user-select-none" :css-focus="focus" @click="onClick">python3</span>
    <div></div>
  </div>
</template>

<script>
export default {
  props: {
    focus: Boolean
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

.navigationpy-container {
  height: 16px;
  display: flex;
  align-items: center;
  > * {
    position: relative;
    left: 0px;
    top: -8px;
  }
  > div {
    background: @color-border-light;
    > div {
      position: relative;
      left: 0px;
      top: -8px;
      height: 16px;
    }
  }
  > div:nth-of-type(1) {
    width: 12px;
    height: 1px;
  }
  > div:nth-of-type(2) {
    width: 8px;
    height: 1px;
    > div {
      cursor: se-resize;
    }
  }
  > div:nth-of-type(3) {
    flex-grow: 1;
    height: 1px;
    pointer-events: none;
  }
  > span {
    cursor: se-resize;
  }
  .navigationpy-icon {
    width: 16px;
    height: 16px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    background-image: url('/static/icons/terminal.png');
  }
  .navigationpy-icon[css-focus] {
    filter: brightness(147%);
  }
  .navigationpy-text {
    font-size: 14px;
    font-family: 'Wawati SC';
    color: @color-text;
  }
  .navigationpy-text[css-focus] {
    color: @color-text-light;
  }
}
</style>
