<template>
  <div class="bytes32-container">
    <span :class="!sameAt(3)?'bytes32-changed':''">{{hexAt(3)}}</span>
    <span>&nbsp;</span>
    <span :class="!sameAt(2)?'bytes32-changed':''">{{hexAt(2)}}</span>
    <span>&nbsp;</span>
    <span :class="!sameAt(1)?'bytes32-changed':''">{{hexAt(1)}}</span>
    <span>&nbsp;</span>
    <span :class="!sameAt(0)?'bytes32-changed':''">{{hexAt(0)}}</span>
  </div>
</template>

<script>
function hexAt(int32, index) {
  return "00";
}

function sameAt(int32, _int32, index) {
  return false;
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
  > span {
    color: @color-text;
    font-size: 12px;
  }
  > span.bytes32-changed {
    color: @color-diff-text;
  }
}
</style>
