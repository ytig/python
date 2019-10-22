<template>
  <div class="stack-container" :style="{width:windowWidth+'px'}" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Pager :canSub="page>0&&sp!=null" :canAdd="page<10-1&&sp!=null" @delta="onDelta"></Pager>
    <Navigation :name="'Stack'" :focus="focus" :disable="disable"></Navigation>
    <div ref="stackLayout" class="stack-layout">
      <Empty v-if="items.length==0" :text="'[no data]'" style="padding-top:12px;"></Empty>
      <Bytes v-else v-for="(item, index) in items" :key="index" :lineNumber="item.lineNumber" :highlightNumber="item.highlightNumber" :watchingNumbers="item.watchingNumbers" :value="item.value" :group="8*column" :showString="false" @clickitem="onClickItem"></Bytes>
    </div>
    <Indicator :size="10" :value="page" @input="onClickIndex" :disable="sp==null"></Indicator>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
import Bytes from '@/views/Bytes';

export default {
  data: function() {
    return {
      focus: false,
      disable: true,
      items: [],
      page: 0,
      sp: null,
      oldData: '',
      newData: '',
      itemSelection: null,
      pageCache: {},
      hst: []
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
      return Bytes.measureWidth('+0x000', 8 * this.column, false);
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
    onMouseUp: function(event) {
      if (event.button == 2) {
        var items = [];
        items[items.length] = ['Go back', '⌫', this.hst.length > 0];
        items[items.length] = ['Jump to SP', 'space', this.sp != null && this.page != 0];
        items[items.length] = ['Previous page', '←', this.sp != null && this.page - 1 >= 0];
        items[items.length] = ['Next page', '→', this.sp != null && this.page + 1 < 10];
        this.$menu.alert(event, items, this.onClickMenu);
      }
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
          this.hstGet();
          break;
        case 1:
          if (this.sp != null && this.page != 0) {
            this.onClickIndex(0);
          }
          break;
        case 2:
          if (this.sp != null && this.page - 1 >= 0) {
            this.onClickIndex(this.page - 1);
          }
          break;
        case 3:
          if (this.sp != null && this.page + 1 < 10) {
            this.onClickIndex(this.page + 1);
          }
          break;
      }
    },
    onKeyDown: function(event) {
      var index = [8, 32, 37, 39].indexOf(event.keyCode);
      if (index >= 0) {
        this.onClickMenu(index);
        return true;
      } else {
        return false;
      }
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
      if (this.sp == null) {
        return false;
      }
      var offset = address - this.sp;
      var row = this.$refs.stackLayout ? Math.floor(this.$refs.stackLayout.clientHeight / Bytes.measureHeight()) : 0;
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
      if (this.sp != sp) {
        this.hstDel();
        if (this.sp != null) {
          this.pageCache[this.sp] = this.page;
        }
        this.sp = sp;
        this.page = this.sp in this.pageCache ? this.pageCache[this.sp] : 0;
        this.oldData = '';
        this.newData = stack;
      } else {
        this.oldData = this.newData;
        this.newData = stack;
      }
      this.itemSelection = null;
      this.invalidate();
    },
    onContinue: function() {
      this.disable = true;
    },
    onClickItem: function(...args) {
      this.$emit('clickitem', ...args);
    },
    onDelta: function(delta) {
      this.onClickIndex(this.page + delta);
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
      var row = this.$refs.stackLayout ? Math.floor(this.$refs.stackLayout.clientHeight / Bytes.measureHeight()) : 0;
      var start = page * column * row;
      var end = (page + 1) * column * row;
      var oldData = this.oldData.slice(start, end);
      oldData = oldData.slice(0, oldData.length - (oldData.length % column));
      var newData = this.newData.slice(start, end);
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
          highlightNumber: highlightNumber,
          watchingNumbers: null,
          value: {
            oldBytes: oldBytes,
            newBytes: newBytes
          }
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
  position: relative;
  display: flex;
  flex-direction: column;
  .stack-layout {
    height: 0px;
    flex-grow: 1;
    overflow-y: scroll;
  }
}
</style>
