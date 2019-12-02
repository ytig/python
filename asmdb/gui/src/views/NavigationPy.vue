<template>
  <div class="navigationpy-container">
    <div class="navigationpy-background"></div>
    <div class="navigationpy-icon"></div>
    <div class="navigationpy-text">python3</div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {};
  },
  props: {
    focus: Boolean
  },
  methods: {}
};
</script>

<style lang="less">
@import '~@/styles/theme';

.navigationpy-container {
  height: 32px;
  display: flex;
  align-items: center;
  position: relative;
  .navigationpy-background {
    position: absolute;
    left: 0px;
    bottom: 0px;
    width: 100%;
    height: 16px;
    background: @color-background-light;
  }
  .navigationpy-icon {
    z-index: 1;
    margin-left: 12px;
    width: 16px;
    height: 16px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    background-image: url('/static/icons/terminal.png');
  }
  .navigationpy-text {
    z-index: 1;
    margin-left: 8px;
    color: @color-text;
    font-size: 14px;
    font-family: 'Wawati SC';
  }
}
</style>
