<template>
  <div class="memory-container" :style="{width:windowWidth+'px'}" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" :theme="0" :condition="searchTest" @search="jumpTo"></Search>
    <Navigation :name="'Memory'" :focus="focus" :disable="disable" :gradient="true" @mouseup2="onMouseUp2"></Navigation>
    <div v-show="!show&&trigger" class="memory-empty">press enter and search an address.</div>
    <Recycler ref="recycler" class="memory-recycler" :show="show" :lineHeight="lineHeight" :source="source" @scroll2="onScroll2" #default="props">
      <Bytes :startAddress="source.toStartAddress(props.index)" :lineNumber="source.toLineNumber(props.index)" :highlightNumber="source.toHighlightNumber(props.index,itemSelection)" :watchingNumbers="source.toWatchingNumbers(props.index,watchpoints)" :assignedNumbers="source.toAssignedNumbers(props.index,assigned)" :oldBytes="props.item!=null?props.item.oldBytes:null" :newBytes="props.item!=null?props.item.newBytes:null" :group="8*column" :showString="true" :canvasContext="props.index*lineHeight+';'+props.context" :lazyLayout="props.scrolling" @clickitem="onClickItem"></Bytes>
    </Recycler>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
import Bytes from '@/views/Bytes';

class Source {
  constructor(start, end, group, history) {
    this.pieceOf = 147 * 16;
    this.start = start;
    this.end = end;
    this.group = group;
    this.history = history;
    this.length = Math.ceil((end - start) / group);
    this.loaded = [];
    this.invalidate = 0;
  }

  toStartAddress(index) {
    return this.start + this.group * index;
  }

  toLineNumber(index) {
    var address = this.start + this.group * index;
    return '0x' + address.toString(16).zfill(2 * asmdb.getInstance().UNIT);
  }

  toHighlightNumber(index, highlight) {
    var address = this.start + this.group * index;
    if (highlight != null) {
      var num = highlight - address;
      if (num >= 0 && num < this.group) {
        return num;
      }
    }
    return null;
  }

  toWatchingNumbers(index, watchpoints) {
    var watchingNumbers = [];
    var address = this.start + this.group * index;
    for (var watchpoint of watchpoints) {
      for (var i = 0; i < asmdb.getInstance().UNIT; i++) {
        var num = watchpoint.address + i - address;
        if (num >= 0 && num < this.group) {
          watchingNumbers.push(num);
        }
      }
    }
    return JSON.stringify(watchingNumbers.sort());
  }

  toAssignedNumbers(index, assigned) {
    var assignedNumbers = [];
    var address = this.start + this.group * index;
    for (var asgn of assigned) {
      var num = asgn - address;
      if (num >= 0 && num < this.group) {
        assignedNumbers.push(asgn - address);
      }
    }
    return JSON.stringify(assignedNumbers.sort());
  }

  getRange(index) {
    var offset = this.group * index;
    offset -= offset % this.pieceOf;
    var start = this.start + offset - this.pieceOf;
    var end = start + 3 * this.pieceOf;
    start = Math.max(start, this.start);
    end = Math.min(end, this.end);
    return [start, end];
  }

  onScroll(index) {
    var range = this.getRange(index);
    var ranges = [];
    for (var i = 0; i < Math.ceil((range[1] - range[0]) / this.pieceOf); i++) {
      var start = range[0] + i * this.pieceOf;
      if (this.loaded.indexOf(start) < 0) {
        this.loaded.push(start);
        var end = Math.min(start + this.pieceOf, range[1]);
        if (ranges.length > 0 && ranges[ranges.length - 1][1] == start) {
          ranges[ranges.length - 1][1] = end;
        } else {
          ranges.push([start, end]);
        }
      }
    }
    for (var r of ranges) {
      asmdb.getInstance().mem(r, this.onLoad.bind(this, r[0]));
    }
  }

  onLoad(address, memory) {
    if (memory.length > this.pieceOf) {
      for (var i = 0; i < Math.ceil(memory.length / this.pieceOf); i++) {
        this.onLoad(address + i * this.pieceOf, memory.substring(i * this.pieceOf, (i + 1) * this.pieceOf));
      }
      return;
    }
    if (this.loaded.indexOf(address) < 0) {
      this.loaded.push(address);
    }
    for (var i = 0; i < Math.ceil(memory.length / this.group); i++) {
      var index = (address - this.start) / this.group + i;
      var newBytes = memory.substring(i * this.group, (i + 1) * this.group);
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

  onAssigned(address, value) {
    var index = parseInt((address - this.start) / this.group);
    var offset = address - index * this.group;
    if (index in this) {
      this[index].newBytes = this[index].newBytes.substring(0, offset) + String.fromCharCode(value) + this[index].newBytes.substring(offset + 1);
      this.invalidate++;
    }
  }
}

export default {
  data: function() {
    return {
      focus: false,
      disable: true,
      trigger: false,
      show: false,
      source: null,
      itemSelection: null,
      watchpoints: [],
      assigned: [],
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
      return Bytes.measureWidth(2 + 2 * asmdb.getInstance().UNIT, 8 * this.column, true);
    },
    lineHeight: function() {
      return Bytes.measureHeight();
    }
  },
  created: function() {
    this.source = new Source(...asmdb.getInstance().getMemoryRange(), 8 * this.column, null);
  },
  mounted: function() {
    keyboard.registerWindow(this);
    asmdb.getInstance().registerEvent('memory', this);
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('memory', this);
    keyboard.unregisterWindow(this);
  },
  methods: {
    searchTest: function(address) {
      var range = asmdb.getInstance().getMemoryRange();
      return address >= range[0] && address < range[1];
    },
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
        this.$menu.close();
      }
    },
    onMouseUp2: function(evnet) {
      var items = [];
      items.push(['Go back', '⌫', this.hst.length > 0]);
      items.push(['Search address', '↩︎', true]);
      this.$menu.alert(event, items, this.onClickMenu);
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
        this.itemSelection = null;
        this.$refs.recycler.scrollTo(posn);
        return true;
      }
    },
    jumpTo: function(address) {
      address = Math.min(Math.max(address, this.source.start), this.source.end - 1);
      var index = parseInt((address - this.source.start) / this.source.group);
      var disable = this.disable;
      if (!disable) {
        this.source.onScroll(index);
      }
      requestAnimationFrames(i => {
        if (this._isDestroyed) {
          return true;
        }
        if (!(disable || index in this.source || i >= 2)) {
          return false;
        }
        var posn = {
          index: index,
          offset: -4
        };
        if (!this.show) {
          this.show = true;
          this.itemSelection = address;
          this.$refs.recycler.scrollTo(posn);
        } else {
          this.itemSelection = address;
          var old_posn = this.$refs.recycler.getPosition();
          this.$refs.recycler.scrollTo(posn);
          var new_posn = this.$refs.recycler.getPosition();
          if (old_posn.index != new_posn.index || old_posn.offset != new_posn.offset) {
            this.hstSet(old_posn);
          }
        }
        return true;
      });
      this.requestFocus();
    },
    getRange: function() {
      if (!this.show) {
        return null;
      }
      return this.source.getRange(this.$refs.recycler.getPosition().index);
    },
    onBreak: function(address, memory) {
      this.trigger = true;
      this.disable = false;
      this.assigned.splice(0, this.assigned.length);
      if (!this.show) {
        return;
      }
      this.source = new Source(...asmdb.getInstance().getMemoryRange(), 8 * this.column, this.source);
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
    onAssigned: function(address, value) {
      if (this.assigned.indexOf(address) < 0) {
        this.assigned.push(address);
      }
      this.source.onAssigned(address, value);
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
    z-index: 1;
    left: 12px;
    top: 40px;
    line-height: 18px;
    font-size: 12px;
    color: @color-text-dark;
  }
  .memory-recycler {
    height: 0px;
    flex-grow: 1;
  }
}
</style>
