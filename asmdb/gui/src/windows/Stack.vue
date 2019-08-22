<template>
  <div class="stack-container" :style="{width:windowWidth+'px'}">
    <Navigation :name="'Stack'" :disable="disable"></Navigation>
    <div ref="stackLayout" class="stack-layout">
      <Empty v-if="items.length==0" :text="'[no data]'" style="padding-top:12px;"></Empty>
      <div v-else>
        <div v-for="i in Math.ceil(items.length/2/column)" :key="i-1" class="stack-row">
          <div>+0x{{("000"+(page*pageSize*8*column+(i-1)*8*column).toString(16)).slice(-3)}}</div>
          <div v-for="(item, j) in items.slice((i-1)*2*column,i*2*column)" :key="(i-1)*2*column+j-1" class="stack-column">
            <div class="stack-empty">{{j%2==0?'&nbsp;&nbsp;':'&nbsp;'}}</div>
            <Bytes32 :oldBytes="item[0]" :newBytes="item[1]"></Bytes32>
          </div>
        </div>
      </div>
    </div>
    <Indicator :size="10" :value="page" @input="onClickIndex" :disable="disable2"></Indicator>
  </div>
</template>

<script>
import asmdb from "@/scripts/asmdb.js";

function measureTextWidth(length) {
  return length * 7.224609375;
}

function measureTextHeight() {
  return 14 + 4;
}

function parseHex(hex) {
  var _hex = "";
  for (var i = Math.floor(hex.length / 2) - 1; i >= 0; i--) {
    _hex += hex.slice(2 * i, 2 * (i + 1));
  }
  return parseInt(_hex, 16);
}

export default {
  data: function() {
    return {
      disable: true,
      disable2: true,
      items: [],
      page: 0,
      pageSize: 0,
      dict: {
        sp: null,
        oldData: null,
        newData: null,
        pageCache: {}
      }
    };
  },
  props: {
    column: {
      type: Number,
      default: 1
    }
  },
  computed: {
    windowWidth: function() {
      return 26 + measureTextWidth(6 + 25 * this.column) + 16 * this.column;
    }
  },
  created: function() {
    asmdb.registerEvent("stack", this);
  },
  destroyed: function() {
    asmdb.unregisterEvent("stack", this);
  },
  methods: {
    onBreak: function(sp, stack) {
      this.disable = false;
      this.disable2 = false;
      var dict = this.dict;
      if (dict.sp != sp) {
        if (dict.sp != null) {
          dict.pageCache[dict.sp] = this.page;
        }
        dict.sp = sp;
        this.page = dict.sp in dict.pageCache ? dict.pageCache[dict.sp] : 0;
        dict.oldData = null;
        dict.newData = stack;
      } else {
        dict.oldData = dict.newData;
        dict.newData = stack;
      }
      this.invalidate();
    },
    onContinue: function() {
      this.disable = true;
    },
    onClickIndex: function(newPage) {
      this.page = newPage;
      this.invalidate();
    },
    invalidate: function() {
      this.pageSize = this.$refs.stackLayout ? Math.floor(this.$refs.stackLayout.clientHeight / measureTextHeight()) : 0;
      var page = this.page;
      var column = this.column * 8;
      var row = this.pageSize;
      var items = [];
      var start = page * column * row;
      var end = start + column * row;
      var oldData = this.dict.oldData != null ? this.dict.oldData.slice(2 * start, 2 * end) : "";
      oldData = oldData.slice(0, oldData.length - (oldData.length % 8));
      var newData = this.dict.newData != null ? this.dict.newData.slice(2 * start, 2 * end) : "";
      newData = newData.slice(0, newData.length - (newData.length % 8));
      for (var i = 0; i < newData.length / 8; i++) {
        var new_data = parseHex(newData.slice(8 * i, 8 * (i + 1)));
        var old_data = null;
        if (i < oldData.length / 8) {
          old_data = parseHex(oldData.slice(8 * i, 8 * (i + 1)));
        }
        items[items.length] = [old_data, new_data];
      }
      this.items.splice(0, this.items.length, ...items);
    }
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.stack-container {
  display: flex;
  flex-direction: column;
  .stack-layout {
    flex-grow: 1;
    height: 0px;
    overflow-y: scroll;
    .stack-row {
      display: flex;
      align-items: center;
      margin-bottom: 4px;
      > *:first-child {
        padding-left: 12px;
        color: @color-darker-text;
        font-size: 12px;
      }
      > *:last-child {
        padding-right: 12px;
      }
      .stack-column {
        display: flex;
        > *:first-child {
          font-size: 12px;
        }
      }
    }
  }
}
</style>
