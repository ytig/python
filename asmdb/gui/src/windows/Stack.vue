<template>
  <div class="stack-container" :style="{width:windowWidth+'px'}" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Pager :canSub="page>0&&sp!=null" :canAdd="page<10-1&&sp!=null" @delta="onDelta"></Pager>
    <Navigation :name="'Stack'" :focus="focus" :disable="disable" @mouseup2="onMouseUp2"></Navigation>
    <div ref="stackLayout" class="stack-layout">
      <div class="stack-draw" :style="{width:windowWidth+'px',height:items.length*lineHeight+'px'}">
        <canvas ref="canvas"></canvas>
      </div>
      <Bytes class="stack-item" v-for="(item, index) in items" :key="index" :startAddress="item.startAddress" :lineNumber="item.lineNumber" :highlightNumber="item.highlightNumber" :watchingNumbers="item.watchingNumbers" :assignedNumbers="item.assignedNumbers" :oldBytes="item.oldBytes" :newBytes="item.newBytes" :group="8*column" :showString="false" :canvasContext="index*lineHeight+';'+context" :lazyLayout="false" @clickitem="onClickItem"></Bytes>
    </div>
    <Indicator :size="10" :value="page" @input="onClickIndex" :disable="sp==null"></Indicator>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import resize from '@/scripts/resize';
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
      watchpoints: [],
      assigned: [],
      context: '',
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
      return Bytes.measureWidth(6, 8 * this.column, false);
    },
    lineHeight: function() {
      return Bytes.measureHeight();
    }
  },
  mounted: function() {
    var canvas = this.$refs.canvas;
    var width = this.windowWidth;
    var height = screen.height;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    this.context = '' + setContext(canvas, 0, height);
    keyboard.registerWindow(this);
    resize.registerEvent(this);
    asmdb.getInstance().registerEvent('stack', this);
  },
  beforeDestroy: function() {
    delContext(this.$refs.canvas);
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('stack', this);
    resize.unregisterEvent(this);
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
        this.$menu.close();
      }
    },
    onMouseUp2: function(evnet) {
      var items = [];
      items.push(['Go back', '⌫', this.hst.length > 0]);
      items.push(['Return to SP', 'space', this.sp != null && this.page != 0]);
      items.push(['Previous page', '←', this.sp != null && this.page - 1 >= 0]);
      items.push(['Next page', '→', this.sp != null && this.page + 1 < 10]);
      this.$menu.alert(event, items, this.onClickMenu);
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
    onResize: function() {
      var row = Math.floor(this.$refs.stackLayout.clientHeight / Bytes.measureHeight());
      if (this.items.length >= row) {
        return;
      }
      this.itemSelection = null;
      this.invalidate();
    },
    hstDel: function() {
      this.hst.splice(0, this.hst.length);
    },
    hstSet: function(posn) {
      const maxHst = 9;
      while (this.hst.length >= maxHst) {
        this.hst.splice(0, 1);
      }
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
      var row = Math.floor(this.$refs.stackLayout.clientHeight / Bytes.measureHeight());
      if (offset < 0 || offset >= 10 * row * this.column * 8) {
        return false;
      }
      var index = Math.floor(offset / (row * this.column * 8));
      if (this.page != index) {
        this.hstSet({ page: this.page });
      }
      this.itemSelection = offset;
      this.page = index;
      this.invalidate();
      this.requestFocus();
      return true;
    },
    onBreak: function(sp, stack) {
      this.disable = false;
      this.assigned.splice(0, this.assigned.length);
      if (this.sp != sp) {
        this.hstDel();
        if (this.sp != null) {
          this.pageCache[this.sp] = this.page;
          if (this.page == 0) {
            delete this.pageCache[this.sp];
          }
        }
        this.sp = sp;
        this.page = this.sp in this.pageCache ? this.pageCache[this.sp] : 0;
        this.oldData = '';
        this.newData = stack;
        this.itemSelection = null;
      } else {
        this.oldData = this.newData;
        this.newData = stack;
      }
      this.invalidate();
    },
    onContinue: function() {
      this.disable = true;
      if (this.itemSelection != null) {
        this.itemSelection = null;
        this.invalidate();
      }
    },
    onWatchpoints: function(watchpoints) {
      this.watchpoints = watchpoints;
      this.invalidate();
    },
    onAssigned: function(address, value) {
      if (this.sp == null) {
        return;
      }
      var offset = address - this.sp;
      if (offset >= 0 && offset < this.newData.length) {
        if (this.assigned.indexOf(address) < 0) {
          this.assigned.push(address);
        }
        this.newData = this.newData.substring(0, offset) + String.fromCharCode(value) + this.newData.substring(offset + 1);
        this.invalidate();
      }
    },
    onClickItem: function(...args) {
      this.$emit('clickitem', ...args);
    },
    onDelta: function(delta) {
      this.onClickIndex(this.page + delta);
    },
    onClickIndex: function(newPage) {
      this.page = newPage;
      this.itemSelection = null;
      this.invalidate();
    },
    invalidate: function() {
      var page = this.page;
      var column = this.column * 8;
      var row = Math.floor(this.$refs.stackLayout.clientHeight / Bytes.measureHeight());
      var start = page * column * row;
      var end = (page + 1) * column * row;
      var oldData = this.oldData.substring(start, end);
      oldData = oldData.substring(0, oldData.length - (oldData.length % column));
      var newData = this.newData.substring(start, end);
      newData = newData.substring(0, newData.length - (newData.length % column));
      var items = [];
      for (var i = 0; i < newData.length / column; i++) {
        var newBytes = newData.substring(i * column, (i + 1) * column);
        var oldBytes = oldData.substring(i * column, (i + 1) * column);
        var lineNumber = start + i * column;
        var startAddress = this.sp + lineNumber;
        var highlightNumber = this.itemSelection != null ? this.itemSelection - lineNumber : -1;
        if (highlightNumber < 0 || highlightNumber >= column) {
          highlightNumber = null;
        }
        var watchingNumbers = [];
        for (var watchpoint of this.watchpoints) {
          for (var j = 0; j < asmdb.getInstance().UNIT; j++) {
            var num = watchpoint.address + j - startAddress;
            if (num >= 0 && num < column) {
              watchingNumbers.push(num);
            }
          }
        }
        var assignedNumbers = [];
        for (var asgn of this.assigned) {
          var num = asgn - startAddress;
          if (num >= 0 && num < column) {
            assignedNumbers.push(num);
          }
        }
        lineNumber = '+0x' + lineNumber.toString(16).zfill(3);
        items.push({
          startAddress: startAddress,
          lineNumber: lineNumber,
          highlightNumber: highlightNumber,
          watchingNumbers: JSON.stringify(watchingNumbers.sort()),
          assignedNumbers: JSON.stringify(assignedNumbers.sort()),
          oldBytes: oldBytes,
          newBytes: newBytes
        });
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
    position: relative;
    height: 0px;
    flex-grow: 1;
    overflow-y: scroll;
    .stack-draw {
      position: absolute;
      overflow: hidden;
      pointer-events: none;
    }
    .stack-item {
      position: relative;
      z-index: 1;
    }
  }
}
</style>
