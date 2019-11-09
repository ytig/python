<template>
  <div class="memory-container" :style="{width:windowWidth+'px'}" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" @search="onSearch"></Search>
    <Navigation :name="'Memory'" :focus="focus" :disable="disable" :gradient="true"></Navigation>
    <Empty v-show="!show" class="memory-empty" :text="'[no data]'"></Empty>
    <Recycler ref="recycler" class="memory-recycler" :show="show" :lineHeight="lineHeight" :source="source" @scroll2="onScroll2" #default="props">
      <Bytes :lineNumber="source.toLineNumber(props.index)" :highlightNumber="source.toHighlightNumber(props.index,itemSelection)" :watchingNumbers="source.toWatchingNumbers(props.index,watchpoints)" :value="props.item" :group="8*column" :showString="true" :canvasContext="props.index+';'+props.context" :lazyLayout="props.scrolling" @clickitem="onClickItem"></Bytes>
    </Recycler>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
import Bytes from '@/views/Bytes';
const pieceOf = 2400;

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
    return '0x' + address.toString(16).zfill(2 * asmdb.asmUnit);
  }

  toHighlightNumber(index, highlight) {
    var address = this.start + this.group * index;
    if (highlight != null) {
      return highlight - address;
    }
    return null;
  }

  toWatchingNumbers(index, watchpoints) {
    var watchingNumbers = [];
    var address = this.start + this.group * index;
    for (var watchpoint of watchpoints) {
      for (var i = 0; i < asmdb.asmUnit; i++) {
        watchingNumbers.push(watchpoint.address + i - address);
      }
    }
    return JSON.stringify(watchingNumbers.sort());
  }

  getRange(index) {
    var offset = this.group * index;
    offset -= offset % pieceOf;
    var start = this.start + offset - pieceOf;
    var end = start + 3 * pieceOf;
    start = Math.max(start, this.start);
    end = Math.min(end, this.end);
    return [start, end];
  }

  onScroll(index) {
    var range = this.getRange(index);
    var ranges = [];
    for (var i = 0; i < Math.ceil((range[1] - range[0]) / pieceOf); i++) {
      var start = range[0] + i * pieceOf;
      if (this.loaded.indexOf(start) < 0) {
        this.loaded.push(start);
        var end = Math.min(start + pieceOf, range[1]);
        if (ranges.length > 0 && ranges[ranges.length - 1][1] == start) {
          ranges[ranges.length - 1][1] = end;
        } else {
          ranges.push([start, end]);
        }
      }
    }
    for (var r of ranges) {
      asmdb.xb(r, this.onLoad.bind(this, r[0]));
    }
  }

  onLoad(address, memory) {
    if (memory.length > pieceOf) {
      for (var i = 0; i < Math.ceil(memory.length / pieceOf); i++) {
        this.onLoad(address + i * pieceOf, memory.slice(i * pieceOf, (i + 1) * pieceOf));
      }
      return;
    }
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
      show: false,
      source: null,
      itemSelection: null,
      watchpoints: [],
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
      return Bytes.measureWidth(2 + 2 * asmdb.asmUnit, 8 * this.column, true);
    },
    lineHeight: function() {
      return Bytes.measureHeight();
    }
  },
  created: function() {
    this.source = new Source(0, Math.pow(16, 2 * asmdb.asmUnit), 8 * this.column, null);
  },
  mounted: function() {
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
    hstSet: function(posn) {
      const maxHst = 147;
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
        this.itemSelection = null;
        this.$refs.recycler.scrollTo(posn);
        return true;
      }
    },
    jumpTo: function(address) {
      address = Math.min(Math.max(address, this.source.start), this.source.end - 1);
      var index = parseInt((address - this.source.start) / this.source.group);
      var old_posn = null;
      if (!this.show) {
        this.show = true;
      } else {
        old_posn = this.$refs.recycler.getPosition();
      }
      this.itemSelection = address;
      this.$refs.recycler.scrollTo({
        index: index,
        offset: -4
      });
      if (old_posn != null) {
        var new_posn = this.$refs.recycler.getPosition();
        if (old_posn.index != new_posn.index || old_posn.offset != new_posn.offset) {
          this.hstSet(old_posn);
        }
      }
      this.requestFocus();
    },
    getRange: function() {
      if (!this.show) {
        return null;
      }
      return this.source.getRange(this.$refs.recycler.getPosition().index);
    },
    onBreak: function(address, memory) {
      this.disable = false;
      if (!this.show) {
        return;
      }
      this.source = new Source(0, Math.pow(16, 2 * asmdb.asmUnit), 8 * this.column, this.source);
      if (Boolean(memory)) {
        this.source.onLoad(address, memory);
      }
      this.source.onScroll(this.$refs.recycler.getPosition().index);
    },
    onContinue: function() {
      this.disable = true;
      this.itemSelection = null;
    },
    onWatchpoints: function(watchpoints) {
      this.watchpoints = watchpoints;
    },
    onScroll2: function(position) {
      if (this.disable) {
        return;
      }
      this.source.onScroll(position.index);
    },
    onClickItem: function(...args) {
      this.$emit('clickitem', ...args);
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
    height: 0px;
    flex-grow: 1;
  }
}
</style>
