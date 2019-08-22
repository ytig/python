<template>
  <div class="bytes32-container" :css-type="bytesType">
    <div :css-changed="''+!sameAt(3)">{{hexAt(3)}}</div>
    <div class="bytes32-empty">&nbsp;</div>
    <div :css-changed="''+!sameAt(2)">{{hexAt(2)}}</div>
    <div class="bytes32-empty">&nbsp;</div>
    <div :css-changed="''+!sameAt(1)">{{hexAt(1)}}</div>
    <div class="bytes32-empty">&nbsp;</div>
    <div :css-changed="''+!sameAt(0)">{{hexAt(0)}}</div>
  </div>
</template>

<script>
function hexAt(int32, index) {
  var hex = ('00000000' + int32.toString(16)).slice(-8);
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
  computed: {
    bytesType: function() {
      var i = this.newBytes % 16;
      if (i == 0 || i == 1) {
        return 'assembly';
      }
      if (i == 2) {
        return 'stack';
      }
      if (i == 3 || i == 4) {
        return 'memory';
      }
      return 'none';
    }
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
@import '~@/styles/theme.less';

.bytes32-container {
  display: flex;
  cursor: pointer;
  > div {
    font-size: 12px;
    padding: 0px 1px;
  }
  .bytes32-empty {
    padding: 0px 0px;
  }
}

.bytes32-container[css-type='none'] {
  cursor: default;
  > div {
    color: @color-text;
  }
  > div[css-changed='true'] {
    color: @color-background;
    background: @color-text;
  }
}

.bytes32-container[css-type='assembly'] {
  > div {
    color: @color-text2;
  }
  > div[css-changed='true'] {
    color: @color-background;
    background: @color-text2;
  }
}

.bytes32-container[css-type='stack'] {
  > div {
    color: @color-text3;
  }
  > div[css-changed='true'] {
    color: @color-background;
    background: @color-text3;
  }
}

.bytes32-container[css-type='memory'] {
  > div {
    color: @color-text4;
  }
  > div[css-changed='true'] {
    color: @color-background;
    background: @color-text4;
  }
}
</style>
