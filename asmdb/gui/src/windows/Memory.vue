<template>
  <div class="memory-container" :style="{width:windowWidth+'px'}" @mousedown="requestFocus" @mouseup="onMouseUp($event)">
    <Navigation :name="'Memory'" :focus="focus" :disable="disable"></Navigation>
    <div ref="memoryLayout" class="memory-layout">
      <Empty v-if="items.length==0" :text="newAddr==null?'[no data]':'[pulling data]'" style="padding-top:12px;"></Empty>
      <Bytes v-else v-for="item in items" :key="item.lineNumber" :value="item" @clickitem="onClickItem"></Bytes>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
const groupBy = 4; //4or8
const pieceOf = 512;

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
      newAddr: 2048, //for test
      oldData: '',
      newData: '',
      itemSelection: null,
      hst: []
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
      return 24 + measureTextWidth(2 + (8 * groupBy) / 4 + 25 * this.column + 2 + 8 * this.column) + 16 * this.column;
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
    },
    onMouseUp: function(event) {
      if (event.button == 2) {
        var items = [];
        items[items.length] = ['Go back', '⌫', this.hst.length > 0];
        items[items.length] = ['Search address', '↩︎', true]; //todo
        this.$menu.alert(event, items, this.onClickMenu);
      }
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
          this.hstGet();
          break;
        case 1:
          console.log('todo ea input');
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
      //todo
    },
    getRange: function() {
      if (this.newAddr == null) {
        return null;
      }
      return [this.newAddr, this.newAddr + 4 * pieceOf];
    },
    onBreak: function(addr, memory) {
      this.disable = false;
      if (this.newAddr == addr) {
        this.oldAddr = this.newAddr;
        this.oldData = this.newData;
        this.newData = memory;
        this.invalidate();
      } else {
        //todo
      }
    },
    onContinue: function() {
      this.disable = true;
    },
    onXB: function(addr, memory) {
      //todo
    },
    onClickItem: function(...args) {
      this.$emit('clickitem', ...args);
    },
    invalidate: function() {
      //todo
      var column = this.column * 8;
      var items = [];
      for (var i = 0; i < this.newData.length / column; i++) {
        var newBytes = this.newData.slice(i * column, (i + 1) * column);
        var lineNumber = '0x' + (this.newAddr + i * column).toString(16).zfill(2 * groupBy);
        items[items.length] = {
          lineNumber: lineNumber,
          oldBytes: '',
          newBytes: newBytes,
          showString: true,
          highlightNumber: null
        };
      }
      this.items.splice(0, this.items.length, ...items);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.memory-container {
  display: flex;
  flex-direction: column;
  .memory-layout {
    flex-grow: 1;
    height: 0px;
    overflow: scroll;
  }
}
</style>
