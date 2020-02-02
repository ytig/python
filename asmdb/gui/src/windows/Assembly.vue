<template>
  <div class="assembly-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" :theme="0" :condition="searchTest" @search="jumpTo"></Search>
    <Navigation :name="'Assembly'" :label="label" :focus="focus" :disable="disable" :gradient="true" @mouseup2="onMouseUp2"></Navigation>
    <div class="assembly-column">
      <div class="assembly-row">
        <Scroller v-if="source!=null" ref="scroller" class="assembly-scroller" :source="source" @scroll2="onScroll2" #default="props">
          <Byte v-if="props.item.type=='byte'" :address="props.item.address" :value="props.item.value" :highlight="source.toContains(props.item,itemSelection)" :running="source.toContains(props.item,pc)" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></Byte>
          <Instruction v-if="props.item.type=='instruction'" :address="props.item.address" :mnemonic="props.item.mnemonic" :op_str="props.item.op_str" :comment="source.toInstructionComment(props.item,breakpoints)" :highlight="source.toContains(props.item,itemSelection)" :running="source.toContains(props.item,pc)" :breaking="source.toInstructionBreaking(props.item,breakpoints)" :group="instructionGroup" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></Instruction>
        </Scroller>
      </div>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
import Byte from '@/views/Byte';
import Instruction from '@/views/Instruction';
const MIN_OFFSET = 4;

function getFloatHeight(el) {
  var height = 0;
  for (var node of el.parentNode.childNodes) {
    if (node == el) {
      continue;
    }
    if (node.attributes && 'float' in node.attributes) {
      height = Math.max(height, node.clientHeight);
    }
  }
  return height;
}

function getRange(address) {
  const pieceOf = 150 * asmdb.getInstance().UNIT;
  var range = asmdb.getInstance().getAssemblyRange();
  var offset = address - range[0];
  offset -= offset % pieceOf;
  var start = range[0] + offset - pieceOf;
  var end = start + 3 * pieceOf;
  start = Math.max(start, range[0]);
  end = Math.min(end, range[1]);
  return [start, end];
}

class Source {
  constructor(address, assembly) {
    for (var i = 0; i < assembly.length; i++) {
      if (address >= assembly[i].address && address < assembly[i].address + assembly[i].size) {
        break;
      }
    }
    for (var j = 0; i + j < assembly.length; j++) {
      this.append(j, assembly[i + j]);
    }
    for (var j = -1; i + j >= 0; j--) {
      this.append(j, assembly[i + j]);
    }
    var range = getRange(address);
    this.pieceOf = 150 * asmdb.getInstance().UNIT;
    this.minIndex = -i;
    this.minAddress = range[0];
    this.minLoading = false;
    this.maxIndex = assembly.length - i;
    this.maxAddress = range[1];
    this.maxLoading = false;
    this.invalidate = 0;
  }

  append(index, value) {
    value.height = {
      byte: Byte,
      instruction: Instruction
    }[value.type].measureHeight(value);
    this[index] = value;
  }

  toContains(item, address) {
    if (address == null) {
      return false;
    }
    return address >= item.address && address < item.address + item.size;
  }

  toInstructionBreaking(item, breakpoints) {
    for (var breakpoint of breakpoints) {
      if (breakpoint.address >= item.address && breakpoint.address < item.address + item.size) {
        if (breakpoint.disable) {
          return 2;
        }
        return 1;
      }
    }
    return 0;
  }

  toInstructionComment(item, breakpoints) {
    for (var breakpoint of breakpoints) {
      if (breakpoint.address >= item.address && breakpoint.address < item.address + item.size) {
        return breakpoint.comment;
      }
    }
    return '';
  }

  getIndex(address) {
    for (var i = this.minIndex; i < this.maxIndex; i++) {
      if (address >= this[i].address && address < this[i].address + this[i].size) {
        return i;
      }
    }
    return null;
  }

  getOffset(position) {
    var offset = 0;
    if (position.index >= 0) {
      for (var i = 0; i < position.index; i++) {
        offset += this[i].height;
      }
    } else {
      for (var i = position.index; i < 0; i++) {
        offset -= this[i].height;
      }
    }
    return offset + position.offset;
  }

  getPosn(position) {
    for (var i = position.index; i < this.maxIndex; i++) {
      if (this[i].size > 0) {
        return {
          address: this[i].address,
          offset: this.getOffset(position) - this.getOffset({ index: i, offset: 0 })
        };
      }
    }
    return null;
  }

  onScroll(index) {
    var preLoad = 150;
    if (index - this.minIndex <= preLoad) {
      if (!this.minLoading) {
        this.minLoading = true;
        var start = Math.max(this.minAddress - this.pieceOf, asmdb.getInstance().getAssemblyRange()[0]);
        if (start < this.minAddress) {
          var range = [start, this.minAddress];
          asmdb.getInstance().asm(range, assembly => {
            this.minLoading = false;
            this.minAddress = range[0];
            for (var i = assembly.length - 1; i >= 0; i--) {
              this.append(--this.minIndex, assembly[i]);
            }
          });
        }
      }
    } else if (this.maxIndex - 1 - index <= preLoad) {
      if (!this.maxLoading) {
        this.maxLoading = true;
        var end = Math.min(this.maxAddress + this.pieceOf, asmdb.getInstance().getAssemblyRange()[1]);
        if (end > this.maxAddress) {
          var range = [this.maxAddress, end];
          asmdb.getInstance().asm(range, assembly => {
            this.maxLoading = false;
            this.maxAddress = range[1];
            for (var i = 0; i < assembly.length; i++) {
              this.append(this.maxIndex++, assembly[i]);
            }
          });
        }
      }
    }
  }
}

export default {
  data: function() {
    return {
      focus: false,
      disable: true,
      label: null,
      pc: null,
      source: null,
      itemSelection: null,
      breakpoints: [],
      counter: 0,
      incomplete: 0,
      counter2: 0,
      hst: []
    };
  },
  computed: {
    instructionGroup: function() {
      return 7;
    }
  },
  mounted: function() {
    keyboard.registerWindow(this);
    asmdb.getInstance().registerEvent('assembly', this);
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('assembly', this);
    keyboard.unregisterWindow(this);
  },
  methods: {
    searchTest: function(address) {
      var range = asmdb.getInstance().getAssemblyRange();
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
      items.push(['Return to PC', 'space', this.needReturnTo()]);
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
        case 2:
          if (this.needReturnTo()) {
            this.returnTo();
          }
          break;
      }
    },
    onKeyDown: function(event) {
      var index = [8, 13, 32].indexOf(event.keyCode);
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
        var range = getRange(posn.address);
        var counter2 = ++this.counter2;
        asmdb.getInstance().asm(range, assembly => {
          if (counter2 != this.counter2 || this._isDestroyed) {
            return;
          }
          this.counter++;
          this.incomplete = 0;
          this.itemSelection = null;
          this.source = new Source(posn.address, assembly);
          this.$nextTick(() => {
            this.$refs.scroller.scrollBy(posn.offset);
          });
        });
        return true;
      }
    },
    jumpTo: function(address) {
      var range = getRange(address);
      var counter2 = ++this.counter2;
      asmdb.getInstance().asm(range, assembly => {
        if (counter2 != this.counter2 || this._isDestroyed) {
          return;
        }
        var old_posn = this.source != null ? this.source.getPosn(this.$refs.scroller.getPosition()) : null;
        this.counter++;
        this.incomplete = 0;
        this.itemSelection = address;
        this.source = new Source(address, assembly);
        this.$nextTick(() => {
          this.$refs.scroller.scrollBy(-MIN_OFFSET);
          if (old_posn != null) {
            var new_posn = this.source.getPosn(this.$refs.scroller.getPosition());
            if (new_posn == null || old_posn.address != new_posn.address || old_posn.offset != new_posn.offset) {
              this.hstSet(old_posn);
            }
          }
        });
      });
      this.requestFocus();
    },
    needReturnTo: function() {
      if (this.pc == null) {
        return false;
      }
      var address = this.pc;
      var index = this.source.getIndex(address);
      if (index != null) {
        var delta = this.source.getOffset({ index: index, offset: -MIN_OFFSET }) - this.source.getOffset(this.$refs.scroller.getPosition());
        return delta - this.incomplete != 0;
      } else {
        return true;
      }
    },
    returnTo: function() {
      if (this.pc == null) {
        return;
      }
      var address = this.pc;
      var index = this.source.getIndex(address);
      if (index != null) {
        var delta = this.source.getOffset({ index: index, offset: -MIN_OFFSET }) - this.source.getOffset(this.$refs.scroller.getPosition());
        this.smoothScrollBy(delta);
      } else {
        var range = getRange(address);
        var counter2 = ++this.counter2;
        asmdb.getInstance().asm(range, assembly => {
          if (counter2 != this.counter2 || this._isDestroyed) {
            return;
          }
          this.counter++;
          this.incomplete = 0;
          this.itemSelection = null;
          this.source = new Source(address, assembly);
          this.$nextTick(() => {
            this.$refs.scroller.scrollBy(-MIN_OFFSET);
          });
        });
      }
    },
    smoothScrollBy: function(deltaY) {
      var duration = 147 + 147 * Math.min(Math.abs(deltaY) / screen.height, 1);
      var maxi = Math.ceil((duration * 3) / 50);
      var counter = this.counter;
      this.incomplete = deltaY;
      requestAnimationFrames(i => {
        if (counter != this.counter || this._isDestroyed) {
          return true;
        }
        var value = ++i / maxi;
        var oldy = deltaY - this.incomplete;
        var newy = parseInt(deltaY * value);
        if (oldy != newy) {
          this.$refs.scroller.scrollBy(newy - oldy);
          this.incomplete = deltaY - newy;
        }
        return !(i < maxi);
      });
    },
    getRange: function(pc) {
      return getRange(pc);
    },
    getMark: function() {
      if (this.source != null) {
        var index = this.source.getIndex(this.pc);
        if (index != null) {
          var mark = this.source.getOffset({ index: index, offset: 0 }) - this.source.getOffset(this.$refs.scroller.getPosition());
          mark -= this.incomplete;
          var maxOffset = this.$refs.scroller.$el.clientHeight - getFloatHeight(this.$el);
          if (mark >= MIN_OFFSET && mark + this.source[index].height <= maxOffset) {
            return mark;
          }
        }
      }
      return MIN_OFFSET;
    },
    onBreak: function(pc, assembly) {
      this.disable = false;
      this.hstDel();
      var mark = this.getMark();
      var posn = this.source != null ? this.source.getPosn(this.$refs.scroller.getPosition()) : null;
      this.counter++;
      this.incomplete = 0;
      this.pc = pc;
      this.source = new Source(pc, assembly);
      this.$nextTick(() => {
        var start = -mark;
        var end = -mark;
        if (posn != null) {
          var index = this.source.getIndex(posn.address);
          if (index != null) {
            var offset = this.source.getOffset({ index: index, offset: posn.offset });
            start = offset;
          }
        }
        this.$refs.scroller.scrollBy(start);
        this.smoothScrollBy(end - start);
      });
    },
    onContinue: function() {
      this.disable = true;
      this.itemSelection = null;
    },
    onBreakpoints: function(breakpoints) {
      this.breakpoints = breakpoints;
    },
    onScroll2: function(position) {
      var current = this.source[position.index];
      var address;
      if (current.height - position.offset > MIN_OFFSET) {
        address = current.address;
      } else {
        address = current.address + current.size;
      }
      this.label = asmdb.getInstance().getAddressLabel(address);
      this.source.onScroll(position.index);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.assembly-container {
  position: relative;
  display: flex;
  flex-direction: column;
  .assembly-column {
    height: 0px;
    flex-grow: 1;
    display: flex;
    .assembly-row {
      width: 0px;
      flex-grow: 1;
      overflow-x: scroll;
      .assembly-scroller {
        height: 100%;
      }
    }
  }
}
</style>
