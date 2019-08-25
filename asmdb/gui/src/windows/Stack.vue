<template>
  <div class="stack-container" :style="{width:windowWidth+'px'}" @mousedown="requestFocus">
    <Navigation :name="'Stack'" :focus="focus" :disable="disable"></Navigation>
    <div ref="stackLayout" class="stack-layout">
      <Empty v-if="items.length==0" :text="'[no data]'" style="padding-top:12px;"></Empty>
      <Bytes v-else v-for="(item, index) in items" :key="index" :value="item" @clickitem="onClickItem"></Bytes>
    </div>
    <Indicator :size="10" :value="page" @input="onClickIndex" :disable="disable2"></Indicator>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';

function measureTextWidth(length) {
  return length * 7.224609375;
}

function measureTextHeight() {
  return 18;
}

export default {
  data: function() {
    return {
      focus: false,
      disable: true,
      disable2: true,
      items: [],
      itemSelection: null,
      page: 0,
      hst: [],
      dict: {
        sp: null,
        oldData: [],
        newData: [],
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
      return 24 + measureTextWidth(6 + 25 * this.column) + 16 * this.column;
    }
  },
  created: function() {
    keyboard.registerWindow(this);
    asmdb.registerEvent('stack', this);
  },
  destroyed: function() {
    asmdb.unregisterEvent('stack', this);
    keyboard.unregisterWindow(this);
  },
  methods: {
    requestFocus: function() {
      keyboard.requestFocus(this);
    },
    onFocusChanged: function(value) {
      this.focus = value;
    },
    onKeyDown: function(event) {
      switch (event.keyCode) {
        case 8:
          this.hstGet();
          break;
        case 32:
          if (!this.disable2 && this.page != 0) {
            this.onClickIndex(0);
          }
          break;
        case 37:
          if (!this.disable2 && this.page - 1 >= 0) {
            this.onClickIndex(this.page - 1);
          }
          break;
        case 39:
          if (!this.disable2 && this.page + 1 < 10) {
            this.onClickIndex(this.page + 1);
          }
          break;
        default:
          return false;
      }
      return true;
    },
    hstDel: function() {
      this.hst.splice(0, this.hst.length);
    },
    hstSet: function() {
      const maxHst = 147;
      while (this.hst.length >= maxHst) {
        this.hst.splice(0, 1);
      }
      var posn = { page: this.page };
      this.hst.splice(this.hst.length, 0, posn);
    },
    hstGet: function() {
      if (this.hst.length <= 0) {
        return false;
      } else {
        var posn = this.hst.splice(this.hst.length - 1, 1)[0];
        this.page = posn.page;
        this.itemSelection = null;
        this.invalidate();
        return true;
      }
    },
    jumpTo: function(address) {
      if (this.dict.sp == null) {
        return false;
      }
      var offset = address - this.dict.sp;
      var row = this.$refs.stackLayout ? Math.floor(this.$refs.stackLayout.clientHeight / measureTextHeight()) : 0;
      if (offset < 0 || offset >= 10 * row * this.column * 8) {
        return false;
      }
      var index = Math.floor(offset / (row * this.column * 8));
      if (this.page != index) {
        this.hstSet();
      }
      this.itemSelection = offset;
      this.page = index;
      this.invalidate();
      this.requestFocus();
      return true;
    },
    onBreak: function(sp, stack) {
      this.disable = false;
      this.disable2 = false;
      var dict = this.dict;
      if (dict.sp != sp) {
        this.hstDel();
        if (dict.sp != null) {
          dict.pageCache[dict.sp] = this.page;
        }
        dict.sp = sp;
        this.page = dict.sp in dict.pageCache ? dict.pageCache[dict.sp] : 0;
        dict.oldData = [];
        dict.newData = stack;
      } else {
        dict.oldData = dict.newData;
        dict.newData = stack;
      }
      this.itemSelection = null;
      this.invalidate();
    },
    onContinue: function() {
      this.disable = true;
    },
    onClickItem: function(...args) {
      this.$emit('clickitem', ...args);
      this.jumpTo(Math.random() < 0.5 ? 2147 : 300); //for test
    },
    onClickIndex: function(newPage) {
      this.hstSet();
      this.page = newPage;
      this.itemSelection = null;
      this.invalidate();
    },
    invalidate: function() {
      var page = this.page;
      var column = this.column * 8;
      var row = this.$refs.stackLayout ? Math.floor(this.$refs.stackLayout.clientHeight / measureTextHeight()) : 0;
      var start = page * column * row;
      var end = (page + 1) * column * row;
      var oldData = this.dict.oldData.slice(start, end);
      oldData = oldData.slice(0, oldData.length - (oldData.length % column));
      var newData = this.dict.newData.slice(start, end);
      newData = newData.slice(0, newData.length - (newData.length % column));
      var items = [];
      for (var i = 0; i < newData.length / column; i++) {
        var newBytes = newData.slice(i * column, (i + 1) * column);
        var oldBytes = oldData.slice(i * column, (i + 1) * column);
        var lineNumber = start + i * column;
        var highlightNumber = this.itemSelection != null ? this.itemSelection - lineNumber : -1;
        if (highlightNumber < 0 || highlightNumber >= column) {
          highlightNumber = null;
        }
        lineNumber = '+0x' + lineNumber.toString(16).zfill(3);
        items[items.length] = {
          lineNumber: lineNumber,
          oldBytes: oldBytes,
          newBytes: newBytes,
          showString: false,
          highlightNumber: highlightNumber
        };
      }
      this.items.splice(0, this.items.length, ...items);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.stack-container {
  display: flex;
  flex-direction: column;
  .stack-layout {
    flex-grow: 1;
    height: 0px;
    overflow: scroll;
  }
}
</style>
