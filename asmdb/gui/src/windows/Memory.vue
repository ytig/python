<template>
  <div class="memory-container" :style="{width:windowWidth+'px'}" @wheel="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" @search="onSearch"></Search>
    <Navigation :name="'Memory'" :focus="focus" :disable="disable" :gradient="true"></Navigation>
    <Empty v-show="items.length==0" class="memory-empty" :text="newAddr==null?'[no data]':'[pulling data]'"></Empty>
    <Recycler ref="recycler" class="memory-recycler" :items="items" #default="props" @loadmore="onDelta">
      <Bytes :value="props.item" @clickitem="onClickItem"></Bytes>
    </Recycler>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
const asmType = 'arm32';
const pieceOf = 1024;

function groupBy() {
  switch (asmType) {
    case 'arm32':
      return 4;
  }
}

function rangeOf() {
  switch (asmType) {
    case 'arm32':
      return [0, Math.pow(16, 8)];
  }
}

function measureTextWidth(length) {
  return length * 7.224609375;
}

export default {
  data: function() {
    return {
      focus: false,
      disable: true,
      items: [],
      oldAddr: null,
      newAddr: null,
      oldData: '',
      newData: '',
      itemPosition: null,
      itemSelection: null,
      hst: [],
      loadOrNot: [false, false]
    };
  },
  props: {
    column: {
      type: Number,
      default: 2
    }
  },
  computed: {
    windowWidth: function() {
      return Math.ceil(24 + measureTextWidth(2 + (8 * groupBy()) / 4 + 25 * this.column + 2 + 8 * this.column) + 16 * this.column);
    }
  },
  created: function() {
    keyboard.registerWindow(this);
    asmdb.registerEvent('memory', this);
  },
  destroyed: function() {
    asmdb.unregisterEvent('memory', this);
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
        var items = [];
        items[items.length] = ['Go back', '⌫', this.hst.length > 0];
        items[items.length] = ['Search address', '↩︎', true];
        this.$menu.alert(event, items, this.onClickMenu);
      }
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
          this.hstGet();
          break;
        case 1:
          this.$refs.search.show();
          break;
      }
    },
    onKeyDown: function(event) {
      var index = [8, 13].indexOf(event.keyCode);
      if (index >= 0) {
        this.onClickMenu(index);
        return true;
      } else {
        return false;
      }
    },
    onSearch: function(address) {
      this.jumpTo(address);
    },
    hstDel: function() {
      this.hst.splice(0, this.hst.length);
    },
    hstSet: function() {
      const maxHst = 147;
      while (this.hst.length >= maxHst) {
        this.hst.splice(0, 1);
      }
      var posn = {}; //todo save
      this.hst.splice(this.hst.length, 0, posn);
    },
    hstGet: function() {
      if (this.hst.length <= 0) {
        return false;
      } else {
        var posn = this.hst.splice(this.hst.length - 1, 1)[0];
        //todo load
        this.invalidate();
        return true;
      }
    },
    jumpTo: function(address) {
      var ro = rangeOf();
      address = Math.min(Math.max(address, ro[0]), ro[1] - 1);
      var addr = Math.min(Math.max(address - (address % (this.column * 8)) - 1 * pieceOf, ro[0]), ro[1] - 3 * pieceOf);
      this.newAddr = addr;
      this.newData = '';
      if (!this.disable) {
        asmdb.xb(this.getRange(), this.onLoadData);
      }
      this.itemPosition = [parseInt(address / (this.column * 8)), 0];
      this.itemSelection = address;
      this.invalidate();
      this.requestFocus();
      return true;
    },
    getRange: function() {
      if (this.newAddr == null) {
        return null;
      }
      return [this.newAddr, this.newAddr + 3 * pieceOf];
    },
    onBreak: function(addr, memory) {
      this.disable = false;
      var range = this.getRange();
      if (range == null) {
        return;
      }
      if (range[0] != addr || range[1] != addr + memory.length) {
        asmdb.xb(range, this.onLoadData);
        return;
      }
      this.oldAddr = this.newAddr;
      this.oldData = this.newData;
      this.newData = memory;
      this.loadOrNot[0] = this.loadOrNot[1] = false;
      this.invalidate();
    },
    onContinue: function() {
      this.disable = true;
    },
    onLoadData: function(addr, memory) {
      var range = this.getRange();
      if (range[0] != addr || range[1] != addr + memory.length) {
        return;
      }
      this.newData = memory;
      this.loadOrNot[0] = this.loadOrNot[1] = false;
      this.invalidate();
    },
    onLoadMore: function(addr, memory) {
      this.$refs.recycler.postStop(() => {
        if (this.newData.length <= 0) {
          return;
        }
        var range = this.getRange();
        if (this.loadOrNot[0] && range[0] == addr + memory.length) {
          this.newAddr -= memory.length;
          this.newData = memory + this.newData.substring(0, this.newData.length - memory.length);
          this.loadOrNot[0] = this.loadOrNot[1] = false;
          this.invalidate();
        }
        if (this.loadOrNot[1] && range[1] == addr) {
          this.newAddr += memory.length;
          this.newData = this.newData.substring(memory.length, this.newData.length) + memory;
          this.loadOrNot[0] = this.loadOrNot[1] = false;
          this.invalidate();
        }
      });
    },
    onClickItem: function(...args) {
      this.$emit('clickitem', ...args);
    },
    onDelta: function(delta) {
      if (this.newAddr == null || this.newData.length <= 0) {
        return;
      }
      var ro = rangeOf();
      var range = this.getRange();
      if (delta < 0) {
        if (!this.loadOrNot[0]) {
          this.loadOrNot[0] = true;
          if (!this.disable && range[0] > ro[0]) {
            asmdb.xb([Math.max(range[0] - pieceOf, ro[0]), range[0]], this.onLoadMore);
          }
        }
      } else {
        this.loadOrNot[0] = false;
      }
      if (delta > 0) {
        if (!this.loadOrNot[1]) {
          this.loadOrNot[1] = true;
          if (!this.disable && range[1] < ro[1]) {
            asmdb.xb([range[1], Math.min(range[1] + pieceOf, ro[1])], this.onLoadMore);
          }
        }
      } else {
        this.loadOrNot[1] = false;
      }
    },
    invalidate: function() {
      //todo
      var column = this.column * 8;
      var items = [];
      var addr = this.getRange()[0];
      for (var i = 0; i < this.newData.length / column; i++) {
        var newBytes = this.newData.slice(i * column, (i + 1) * column);
        var lineNumber = addr + i * column;
        var highlightNumber = this.itemSelection != null ? this.itemSelection - lineNumber : -1;
        if (highlightNumber < 0 || highlightNumber >= column) {
          highlightNumber = null;
        }
        lineNumber = '0x' + lineNumber.toString(16).zfill(2 * groupBy());
        var idx = addr / column + i;
        items[items.length] = {
          idx: idx,
          lineNumber: lineNumber,
          oldBytes: '',
          newBytes: newBytes,
          showString: true,
          highlightNumber: highlightNumber,
          watchingNumbers: null
        };
      }
      this.items.splice(0, this.items.length, ...items);
      var posn = this.$refs.recycler.getPosition();
      if (!posn) {
        posn = this.itemPosition;
      }
      this.items.posn = posn;
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.memory-container {
  position: relative;
  display: flex;
  flex-direction: column;
  .memory-empty {
    position: absolute;
    top: 40px;
    width: 100%;
    padding-top: 12px;
  }
  .memory-recycler {
    flex-grow: 1;
    height: 0px;
    overflow: scroll;
  }
}
</style>
