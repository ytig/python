<template>
  <div class="memory-container" :style="{width:windowWidth+'px'}" @mousedown="requestFocus" @mouseup="onMouseUp($event)">
    <Navigation :name="'Memory'" :focus="focus" :disable="disable"></Navigation>
    <div ref="memoryLayout" class="memory-layout">
      <Empty v-if="items.length==0" :text="ea==null?'[no data]':'[pulling data]'" style="padding-top:12px;"></Empty>
      <Bytes v-else v-for="i in 100" :key="i" :value="{lineNumber:'0x00112233',newBytes:[1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8],showString:true}"></Bytes>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
const groupBy = 4; //4or8
const pieceOf = 256;

function measureTextWidth(length) {
  return length * 7.224609375;
}

export default {
  data: function() {
    return {
      focus: false,
      disable: true,
      items: [],
      ea: null,
      oldData: [],
      newData: [],
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
      if (this.ea == null) {
        return null;
      }
      return [this.ea, this.ea + 4 * pieceOf];
    },
    onBreak: function(ea, memory) {
      this.disable = false;
      if (this.ea == ea) {
        this.oldData = this.newData;
        this.newData = memory;
      } else {
        //todo
      }
      this.invalidate();
    },
    onContinue: function() {
      this.disable = true;
    },
    onXB: function(ea, memory) {
      //todo
    },
    onClickItem: function(...args) {
      this.$emit('clickitem', ...args);
    },
    invalidate: function() {
      //todo
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
