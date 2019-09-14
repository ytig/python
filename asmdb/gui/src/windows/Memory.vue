<template>
  <div class="memory-container" :style="{width:windowWidth+'px'}" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search"></Search>
    <Navigation :name="'Memory'" :focus="focus" :disable="disable" :gradient="true"></Navigation>
    <Empty v-show="items.length==0" class="memory-empty" :text="newAddr==null?'[no data]':'[pulling data]'"></Empty>
    <Recycler ref="recycler" class="memory-recycler" :items="items" #default="props">
      <Bytes :value="props.item" @clickitem="onClickItem"></Bytes>
    </Recycler>
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
      newAddr: 0, //for test
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
      return [this.newAddr, this.newAddr + 5 * pieceOf];
    },
    onBreak: function(addr, memory) {
      this.disable = false;
      if (this.newAddr == addr) {
        this.oldAddr = this.newAddr;
        this.oldData = this.newData;
        this.newData = memory;
        this.invalidate();
        setTimeout(() => {
          this.onLoadMore();
        }, 2000);
      } else {
        //todo
      }
    },
    onContinue: function() {
      this.disable = true;
    },
    onLoadMore: function(addr, memory) {
      //todo
      this.$refs.recycler.postStop(() => {
        var t = 512;
        this.newAddr += t;
        this.newData = this.newData.slice(t, this.newData.length);
        for (var i = 0; i < t; i++) {
          this.newData += 't';
        }
        this.invalidate();
      });
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
        var idx = this.newAddr / column + i;
        items[items.length] = {
          idx: idx,
          lineNumber: lineNumber,
          oldBytes: '',
          newBytes: newBytes,
          showString: true,
          highlightNumber: null,
          watchingNumbers: null
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
