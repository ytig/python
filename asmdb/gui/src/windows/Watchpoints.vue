<template>
  <div class="watchpoints-container" :style="{width:windowWidth+'px'}" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Navigation :name="'Wpoints'" :focus="focus" :gradient="true"></Navigation>
    <Empty v-show="items.length==0" class="watchpoints-empty" :text="'no point'"></Empty>
    <div class="watchpoints-layout">
      <div></div>
      <div class="watchpoints-item" v-for="item in items" :key="item">
        <span></span>
        <span @click="onClickItem(index)">{{item}}</span>
        <span></span>
        <span @click="onSubPoint(index)"></span>
      </div>
      <div class="watchpoints-func">
        <span v-show="items.length<items.max_length" @click="onAddPoint"></span>
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

function measureViewWidth() {
  return Math.ceil(12 + 8 + 8 + measureTextWidth(2 + 2 * asmdb.UNIT) + 32 + 16 + 12);
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
      return measureViewWidth();
    },
    items: function() {
      var items = [];
      for (var watchpoint of this.watchpoints) {
        items.push('0x' + watchpoint.address.toString(16).zfill(2 * asmdb.UNIT));
      }
      items.max_length = asmdb.WLEN;
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
    },
    onClickItem: function(index) {
      this.$emit('clickitem', 1, this.items[index]);
    },
    onSubPoint: function(index) {
      asmdb.wsub(this.watchpoints[index].address);
    },
    onAddPoint: function() {
      //todo
      asmdb.wadd(224);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.watchpoints-container {
  position: relative;
  height: 130px;
  display: flex;
  flex-direction: column;
  .watchpoints-empty {
    position: absolute;
    top: 40px;
  }
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
      > span:nth-child(1) {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: @color-icon-breakpoint;
        margin-right: 8px;
      }
      > span:nth-child(2) {
        font-size: 12px;
        color: @color-text;
        cursor: pointer;
      }
      > span:nth-child(3) {
        flex-grow: 1;
      }
      > span:nth-child(4) {
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
      display: flex;
      flex-direction: row-reverse;
      align-items: center;
      > span {
        width: 16px;
        height: 16px;
        background-size: 16px 16px;
        background-repeat: no-repeat;
        background-position: center center;
        margin-left: 8px;
        margin-top: 1px;
        margin-bottom: 1px;
        cursor: pointer;
      }
      > span:nth-child(1) {
        background-image: url('/static/icons/add.png');
      }
    }
  }
}
</style>
