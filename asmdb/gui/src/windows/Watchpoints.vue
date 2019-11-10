<template>
  <div class="watchpoints-container" :style="{width:windowWidth+'px',height:windowWidth+'px'}" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Navigation :name="'Wpoints'" :focus="focus" :gradient="true"></Navigation>
    <div class="watchpoints-layout">
      <div></div>
      <div class="watchpoints-item" v-for="(item, index) in items" :key="index">
        <span>{{index}}</span>
        <span>{{item}}</span>
        <span></span>
      </div>
      <div class="watchpoints-func">
        <span></span>
      </div>
      <div></div>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';

function measureTextWidth(length) {
  return length * 7.224609375;
}

function measureViewWidth(lineNumberLength) {
  return Math.ceil(4 * 12 + 16 + measureTextWidth(lineNumberLength + 2 + 2 * asmdb.UNIT));
}

export default {
  data: function() {
    return {
      focus: false,
      watchpoints: []
    };
  },
  computed: {
    windowWidth: function() {
      return measureViewWidth(1);
    },
    items: function() {
      var items = [];
      for (var watchpoint of this.watchpoints) {
        items.push('0x' + watchpoint.address.toString(16).zfill(2 * asmdb.UNIT));
        //for test
        items.push('0x' + watchpoint.address.toString(16).zfill(2 * asmdb.UNIT));
        items.push('0x' + watchpoint.address.toString(16).zfill(2 * asmdb.UNIT));
        items.push('0x' + watchpoint.address.toString(16).zfill(2 * asmdb.UNIT));
        items.push('0x' + watchpoint.address.toString(16).zfill(2 * asmdb.UNIT));
        items.push('0x' + watchpoint.address.toString(16).zfill(2 * asmdb.UNIT));
        items.push('0x' + watchpoint.address.toString(16).zfill(2 * asmdb.UNIT));
        items.push('0x' + watchpoint.address.toString(16).zfill(2 * asmdb.UNIT));
      }
      return items;
    }
  },
  mounted: function() {
    keyboard.registerWindow(this);
    asmdb.registerEvent('watchpoints', this);
  },
  destroyed: function() {
    asmdb.unregisterEvent('watchpoints', this);
    keyboard.unregisterWindow(this);
  },
  methods: {
    requestFocus: function() {
      keyboard.requestFocus(this);
    },
    onFocusChanged: function(value) {
      this.focus = value;
    },
    onMouseUp: function(event) {
      if (event.button == 2) {
        this.$menu.alert(event);
      }
    },
    onKeyDown: function(event) {
      return false;
    },
    onWatchpoints: function(watchpoints) {
      this.watchpoints = watchpoints;
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.watchpoints-container {
  display: flex;
  flex-direction: column;
  .watchpoints-layout {
    height: 0px;
    flex-grow: 1;
    overflow-y: scroll;
    padding-left: 12px;
    padding-right: 12px;
    > div:first-child {
      height: 4px;
    }
    > div:last-child {
      height: 9px;
    }
    .watchpoints-item {
      height: 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      > span {
        font-size: 12px;
      }
      > span:nth-child(1) {
        color: @color-text-darker;
      }
      > span:nth-child(2) {
        color: @color-text;
        cursor: pointer;
      }
      > span:nth-child(3) {
        width: 16px;
        height: 16px;
        background-size: 16px 16px;
        background-repeat: no-repeat;
        background-position: center center;
        background-image: url('/static/icons/sub.png');
        cursor: pointer;
      }
    }
    .watchpoints-func {
      height: 18px;
      display: flex;
      flex-direction: row-reverse;
      align-items: center;
      > span {
        width: 16px;
        height: 16px;
        background-size: 16px 16px;
        background-repeat: no-repeat;
        background-position: center center;
        margin-left: 12px;
      }
      > span:nth-child(1) {
        background-image: url('/static/icons/add.png');
        cursor: pointer;
      }
    }
  }
}
</style>
