<template>
  <div class="watchpoints-container" :style="{width:windowWidth+'px'}" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" :theme="1" @search="onAddPoint"></Search>
    <Navigation :name="'Wpoints'" :focus="focus" :gradient="true" @mouseup2="onMouseUp2"></Navigation>
    <Empty v-show="watchpoints.length==0" class="watchpoints-empty" :text="'no point'"></Empty>
    <div class="watchpoints-layout">
      <div></div>
      <div class="watchpoints-item" v-for="point in watchpoints" :key="point.address">
        <span></span>
        <span @click="onClickItem(point)">{{toHex(point.address)}}</span>
        <span></span>
        <div class="watchpoints-icon" @click="onSubPoint(point)"></div>
      </div>
      <div class="watchpoints-func">
        <div v-show="watchpoints.length<wlen" class="watchpoints-icon" @click="onClickMenu(0)"></div>
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
  return Math.ceil(12 + 8 + 8 + measureTextWidth(2 + 2 * asmdb.getInstance().UNIT) + 32 + 16 + 12);
}

export default {
  data: function() {
    return {
      focus: false,
      watchpoints: [],
      wlen: asmdb.getInstance().WLEN
    };
  },
  computed: {
    windowWidth: function() {
      return measureViewWidth();
    }
  },
  mounted: function() {
    keyboard.registerWindow(this);
    asmdb.getInstance().registerEvent('watchpoints', this);
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('watchpoints', this);
    keyboard.unregisterWindow(this);
  },
  methods: {
    toHex: function(address) {
      return '0x' + address.toString(16).zfill(2 * asmdb.getInstance().UNIT);
    },
    requestFocus: function() {
      keyboard.requestFocus(this);
    },
    onFocusChanged: function(value) {
      this.focus = value;
      if (!value) {
        this.$refs.search.dismiss();
      }
    },
    onMouseUp: function(event) {
      if (event.button == 2) {
        this.$menu.close();
      }
    },
    onMouseUp2: function(evnet) {
      var items = [];
      items[items.length] = ['Edit watchpoint', '↩︎', this.watchpoints.length < this.wlen];
      this.$menu.alert(event, items, this.onClickMenu);
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
          if (this.watchpoints.length < this.wlen) {
            this.$refs.search.show();
          }
          break;
      }
    },
    onKeyDown: function(event) {
      var index = [13].indexOf(event.keyCode);
      if (index >= 0) {
        this.onClickMenu(index);
        return true;
      } else {
        return false;
      }
    },
    onWatchpoints: function(watchpoints) {
      this.watchpoints = watchpoints;
    },
    onClickItem: function(point) {
      this.$emit('clickitem', 1, point.address);
    },
    onSubPoint: function(point) {
      asmdb.getInstance().wp([point], []);
    },
    onAddPoint: function(address) {
      address = Math.min(Math.max(address, 0), Math.pow(16, 2 * asmdb.getInstance().UNIT) - 1);
      address -= address % asmdb.getInstance().UNIT;
      asmdb.getInstance().wp([], [{ address: address }]);
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
      > span:nth-of-type(1) {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: @color-icon-breakpoint;
        margin-right: 8px;
      }
      > span:nth-of-type(2) {
        font-size: 12px;
        color: @color-text;
        cursor: pointer;
      }
      > span:nth-of-type(3) {
        flex-grow: 1;
      }
      > div:nth-last-of-type(1) {
        background-image: url('/static/icons/sub.png');
      }
    }
    .watchpoints-func {
      display: flex;
      flex-direction: row-reverse;
      align-items: center;
      > div {
        margin-left: 8px;
        margin-top: 1px;
        margin-bottom: 1px;
      }
      > div:nth-of-type(1) {
        background-image: url('/static/icons/add.png');
      }
    }
  }
  .watchpoints-icon {
    width: 16px;
    height: 16px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    cursor: pointer;
  }
}
</style>
