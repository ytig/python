<template>
  <div class="memory-container" :style="{width:windowWidth+'px'}" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" @search="onSearch"></Search>
    <Navigation :name="'Memory'" :focus="focus" :disable="disable" :gradient="true"></Navigation>
    <!-- <Empty v-show="items.length==0" class="memory-empty" :text="newAddr==null?'[no data]':'[pulling data]'"></Empty> -->
    <Recycler class="memory-recycler" :lineHeight="lineHeight" :source="source" @scroll2="onScroll2" #default="props">
      <Bytes :lineNumber="source.toLineNumber(props.index)" :highlightNumber="source.toHighlightNumber(props.index,itemPosition)" :watchingNumbers="source.toWatchingNumbers(props.index,[])" :value="props.item" :group="8*column" :showString="true" @clickitem="onClickItem"></Bytes>
    </Recycler>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
const asmType = 'arm32';
const pieceOf = 2400;

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

function measureTextHeight() {
  return 18;
}

class Source {
  constructor(start, end, group, history) {
    this.start = start;
    this.end = end;
    this.group = group;
    this.history = history;
    this.length = Math.ceil((end - start) / group);
    this.loaded = [];
    this.invalidate = 0;
  }

  toLineNumber(index) {
    var address = this.start + this.group * index;
    return '0x' + address.toString(16).zfill(2 * groupBy());
  }

  toHighlightNumber(index, highlight) {
    var address = this.start + this.group * index;
    if (highlight != null) {
      return highlight - address;
    }
    return null;
  }

  toWatchingNumbers(index, watching) {
    var _watching = [];
    var address = this.start + this.group * index;
    if (watching != null) {
      for (var addr of watching) {
        _watching.push(addr - address);
      }
    }
    return JSON.stringify(_watching.sort());
  }

  onScroll(index) {
    var offset = this.group * index;
    offset -= offset % pieceOf;
    this.load(offset - pieceOf);
    this.load(offset);
    this.load(offset + pieceOf);
  }

  load(offset) {
    if (offset < 0 || offset >= this.end - this.start) {
      return;
    }
    var start = this.start + offset;
    var end = Math.min(start + pieceOf, this.end);
    if (this.loaded.indexOf(start) >= 0) {
      return;
    }
    this.loaded.push(start);
    asmdb.xb([start, end], this.onLoad.bind(this));
  }

  onLoad(address, memory) {
    if (this.loaded.indexOf(address) < 0) {
      this.loaded.push(address);
    }
    for (var i = 0; i < Math.ceil(memory.length / this.group); i++) {
      var index = (address - this.start) / this.group + i;
      var newBytes = memory.slice(i * this.group, (i + 1) * this.group);
      var oldBytes = null;
      if (this.history != null && index in this.history) {
        oldBytes = this.history[index].newBytes;
      }
      this[index] = {
        oldBytes: oldBytes,
        newBytes: newBytes
      };
    }
    this.invalidate++;
  }
}

export default {
  data: function() {
    return {
      focus: false,
      disable: true,
      items: [],
      source: null,
      itemPosition: null,
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
      return Math.ceil(24 + measureTextWidth(2 + 2 * groupBy() + 25 * this.column + 2 + 8 * this.column) + 16 * this.column);
    },
    lineHeight: function() {
      return measureTextHeight();
    }
  },
  created: function() {
    this.source = new Source(0, Math.pow(16, 2 * groupBy()), 8 * this.column, null);
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
      if (this.newAddr == null) {
        return false;
      }
      const maxHst = 147;
      while (this.hst.length >= maxHst) {
        this.hst.splice(0, 1);
      }
      var posn = null;
      //todo
      this.hst.splice(this.hst.length, 0, posn);
      return true;
    },
    hstGet: function() {
      if (this.hst.length <= 0) {
        return false;
      } else {
        var posn = this.hst.splice(this.hst.length - 1, 1)[0];
        //todo
        this.invalidate();
        return true;
      }
    },
    jumpTo: function(address) {
      this.hstSet();
      //todo
    },
    getRange: function() {
      //todo
    },
    onBreak: function(addr, memory) {
      this.disable = false;
      //todo
      this.invalidate();
    },
    onContinue: function() {
      this.disable = true;
    },
    onScroll2: function(position) {
      if (this.disable) {
        return;
      }
      this.source.onScroll(position.index);
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
  }
}
</style>
