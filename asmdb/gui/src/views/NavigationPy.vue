<template>
  <div class="navigationpy-container">
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
  padding-left: 12px;
  height: 32px;
  display: flex;
  align-items: center;
  .navigationpy-icon {
    width: 16px;
    height: 16px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    background-image: url('/static/icons/terminal.png');
  }
  .navigationpy-text {
    margin-left: 8px;
    color: @color-text;
    font-size: 14px;
    font-family: 'Wawati SC';
  }
}
</style>
