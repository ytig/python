<template>
  <div class="watchpoints-container" :style="{width:windowWidth+'px'}" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" :theme="1" :condition="searchTest" @search="onAddPoint"></Search>
    <Navigation :name="'Wpoints'" :focus="focus" :gradient="true" @mouseup2="onMouseUp2"></Navigation>
    <div class="watchpoints-layout">
      <div></div>
      <div class="watchpoints-item" v-for="point in watchpoints" :key="point.address">
        <span></span>
        <span @click="onClickItem(point)" @mouseup="onMouseUpItem(point, ...arguments)">{{toHex(point.address)}}</span>
        <span class="watchpoints-grow"></span>
        <div class="watchpoints-icon" @click="onSubPoint(point)"></div>
      </div>
      <div class="watchpoints-func">
        <div v-show="watchpoints.length<wlen" class="watchpoints-icon" @click="onClickMenu(1)"></div>
      </div>
      <div></div>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';

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
      return Math.ceil(12 + 8 + 8 + measureLength(2 + 2 * asmdb.getInstance().UNIT) + 32 + 16 + 12);
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
    searchTest: function(address) {
      var range = asmdb.getInstance().getMemoryRange();
      return address >= range[0] && address < range[1];
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
      items.push(['Delete all', '⇧⌫', this.watchpoints.length > 0]);
      items.push(['Edit watchpoint', '↩︎', this.watchpoints.length < this.wlen]);
      this.$menu.alert(event, items, this.onClickMenu);
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
          if (this.watchpoints.length > 0) {
            asmdb.getInstance().wpt(this.watchpoints, []);
          }
          break;
        case 1:
          if (this.watchpoints.length < this.wlen) {
            this.$refs.search.show();
          }
          break;
      }
    },
    onKeyDown: function(event) {
      var d = 0;
      var index = [8].indexOf(event.keyCode);
      if (index >= 0 && !event.altKey && !event.ctrlKey && !event.metaKey && event.shiftKey) {
        this.onClickMenu(index + d);
        return true;
      } else {
        d += 1;
        index = [13].indexOf(event.keyCode);
        if (index >= 0) {
          this.onClickMenu(index + d);
          return true;
        } else {
          return false;
        }
      }
    },
    onWatchpoints: function(watchpoints) {
      this.watchpoints.splice(0, this.watchpoints.length, ...watchpoints);
      this.watchpoints.sort((p1, p2) => {
        return p1.address - p2.address;
      });
    },
    onClickItem: function(point) {
      this.$emit('clickitem', 1, point.address);
    },
    onSubPoint: function(point) {
      asmdb.getInstance().wpt([point], []);
    },
    onAddPoint: function(address) {
      address -= address % asmdb.getInstance().UNIT;
      asmdb.getInstance().wpt([], [{ address: address }]);
    },
    onMouseUpItem: function(point, event) {
      if (event.button == 2) {
        var menu = this.onCreateMenu(point);
        this.$menu.alert(event, menu, i => {
          menu[i].event();
        });
        event.stopPropagation();
      }
    },
    onCreateMenu: function(point) {
      var items = [];
      var intValue = point.address;
      items.push(['Copy', '', true]);
      items[items.length - 1].event = () => {
        emptySelection();
        this.$toast.alert('Text Copied');
        copyText('0x' + intValue.toString(16));
      };
      return items;
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.watchpoints-container {
  position: relative;
  height: 157px;
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
      > span:nth-of-type(1) {
        width: 5px;
        height: 5px;
        border-radius: 999px;
        background: @color-icon-breakpoint;
        margin-right: 8px;
      }
      > span:nth-of-type(2) {
        font-size: 12px;
        color: @color-text;
        cursor: pointer;
      }
      .watchpoints-grow {
        flex-grow: 1;
      }
      .watchpoints-icon {
        margin-left: 12px;
      }
      .watchpoints-icon:nth-last-of-type(1) {
        background-image: url('/static/icons/sub.png');
      }
    }
    .watchpoints-func {
      display: flex;
      flex-direction: row-reverse;
      align-items: center;
      > div {
        margin-left: 12px;
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
