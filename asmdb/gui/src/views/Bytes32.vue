<template>
  <div class="bytes32-container">
    <div :class="!sameAt(3)?'bytes32-changed':''">{{hexAt(3)}}</div>
    <div>&nbsp;</div>
    <div :class="!sameAt(2)?'bytes32-changed':''">{{hexAt(2)}}</div>
    <div>&nbsp;</div>
    <div :class="!sameAt(1)?'bytes32-changed':''">{{hexAt(1)}}</div>
    <div>&nbsp;</div>
    <div :class="!sameAt(0)?'bytes32-changed':''">{{hexAt(0)}}</div>
  </div>
</template>

<script>
function hexAt(int32, index) {
  var hex = ("00000000" + int32.toString(16)).slice(-8);
  return hex.slice(2 * index, 2 * (index + 1));
}

function sameAt(int32, _int32, index) {
  return hexAt(int32, index) == hexAt(_int32, index);
}

export default {
  props: {
    oldBytes: Number,
    newBytes: Number
  },
  methods: {
    hexAt: function(index) {
      return hexAt(this.newBytes, index);
    },
    sameAt: function(index) {
      if (this.oldBytes == null) {
        return true;
      }
      return sameAt(this.newBytes, this.oldBytes, index);
    }
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.bytes32-container {
  display: flex;
  > div {
    color: @color-text;
    font-size: 12px;
  }
  > div.bytes32-changed {
    color: @color-diff-text;
  }
}
</style>
