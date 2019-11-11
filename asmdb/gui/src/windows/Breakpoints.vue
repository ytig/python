<template>
  <div class="breakpoints-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" :theme="1" @search="onAddPoint"></Search>
    <Navigation :name="'Bpoints'" :focus="focus" :gradient="true" @mouseup2="onMouseUp2"></Navigation>
    <Empty v-show="breakpoints.length==0" class="breakpoints-empty" :text="'no point'"></Empty>
    <div class="breakpoints-layout">
      <div></div>
      <div class="breakpoints-item" v-for="point in breakpoints" :key="point.address" :css-disable="point.disable">
        <span></span>
        <span @click="onClickItem(point)">{{toHex(point.address)}}</span>
        <span></span>
        <div class="breakpoints-icon" @click="onTogglePoint(point)"></div>
        <div class="breakpoints-icon" @click="onSubPoint(point)"></div>
      </div>
      <div class="breakpoints-func">
        <div class="breakpoints-icon" @click="onClickMenu(0)"></div>
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
      breakpoints: []
    };
  },
  mounted: function() {
    keyboard.registerWindow(this);
    asmdb.getInstance().registerEvent('breakpoints', this);
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('breakpoints', this);
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
      items[items.length] = ['Edit breakpoint', '↩︎', true];
      this.$menu.alert(event, items, this.onClickMenu);
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
          this.$refs.search.show();
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
    onBreakpoints: function(breakpoints) {
      this.breakpoints = breakpoints;
    },
    onClickItem: function(point) {
      this.$emit('clickitem', 0, point.address);
    },
    onSubPoint: function(point) {
      asmdb.getInstance().bp([point], []);
    },
    onTogglePoint: function(point) {
      point = Object.assign({}, point);
      point.disable = !point.disable;
      asmdb.getInstance().bp([], [point]);
    },
    onAddPoint: function(address) {
      address = Math.min(Math.max(address, 0), Math.pow(16, 2 * asmdb.getInstance().UNIT) - 1);
      asmdb.getInstance().bp([], [{ address: address, disable: false }]);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.breakpoints-container {
  position: relative;
  height: 130px;
  display: flex;
  flex-direction: column;
  .breakpoints-empty {
    position: absolute;
    top: 40px;
  }
  .breakpoints-layout {
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
    .breakpoints-item {
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
      > div {
        margin-left: 12px;
      }
      > div:nth-last-of-type(1) {
        background-image: url('/static/icons/sub.png');
      }
      > div:nth-last-of-type(2) {
        background-image: url('/static/icons/toggle.png');
      }
    }
    .breakpoints-item[css-disable] {
      > span:nth-of-type(1) {
        background: @color-icon-breakpoint2;
      }
    }
    .breakpoints-func {
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
  .breakpoints-icon {
    width: 16px;
    height: 16px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    cursor: pointer;
  }
}
</style>
