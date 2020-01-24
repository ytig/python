<template>
  <div class="assist-input-container">
    <div :style="{backgroundImage:backgroundImage}"></div>
    <input ref="input" type="text" v-model="value" />
  </div>
</template>

<script>
export default {
  props: {
    icon: String,
    value: String,
    assist: Array
  },
  computed: {
    backgroundImage: function() {
      var url = '/static/icons/' + this.icon + '.png';
      return "url('" + url + "')";
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.assist-input-container {
  position: relative;
  height: 32px;
  border-radius: 4px;
  background-color: @color-background-darker;
  box-shadow: inset 0px 2px 8px rgba(0, 0, 0, 0.8);
  > div {
    position: absolute;
    left: 12px;
    top: 8px;
    width: 16px;
    height: 16px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    pointer-events: none;
  }
  > input {
    width: 100%;
    padding-left: 36px;
    padding-right: 12px;
    line-height: 32px;
    font-size: 12px;
    color: @color-text;
    text-overflow: ellipsis;
  }
}
</style>
