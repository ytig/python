<template>
  <div class="breakpoints-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" :theme="1" @search="onAddPoint"></Search>
    <Navigation :name="'Bpoints'" :focus="focus" :gradient="true" @mouseup2="onMouseUp2"></Navigation>
    <Empty v-show="items.length==0" class="breakpoints-empty" :text="'no point'"></Empty>
    <div class="breakpoints-layout">
      <div></div>
      <div class="breakpoints-item" v-for="(item, index) in items" :key="item">
        <span></span>
        <span @click="onClickItem(index)">{{item}}</span>
        <span></span>
        <span @click="onSubPoint(index)"></span>
      </div>
      <div class="breakpoints-func">
        <span @click="onClickMenu(0)"></span>
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
  computed: {
    items: function() {
      var items = [];
      for (var point of this.breakpoints) {
        items.push('0x' + point.address.toString(16).zfill(2 * asmdb.getInstance().UNIT));
      }
      return items;
    }
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
    onClickItem: function(index) {
      this.$emit('clickitem', 0, this.items[index]);
    },
    onSubPoint: function(index) {
      asmdb.getInstance().bp([this.breakpoints[index]], []);
    },
    onAddPoint: function(address) {
      address = Math.min(Math.max(address, 0), Math.pow(16, 2 * asmdb.getInstance().UNIT) - 1);
      asmdb.getInstance().bp([], [{ address: address }]);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.breakpoints-container {
  position: relative;
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
    .breakpoints-func {
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
