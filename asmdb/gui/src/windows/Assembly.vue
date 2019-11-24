<template>
  <div class="assembly-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" :theme="0" :condition="searchTest" @search="jumpTo"></Search>
    <Navigation :name="'Assembly'" :focus="focus" :disable="disable" :gradient="true" @mouseup2="onMouseUp2"></Navigation>
    <div class="assembly-column">
      <div class="assembly-row">
        <Scroller v-if="source!=null" ref="scroller" class="assembly-scroller" :style="{width:windowWidth+'px'}" :source="source" @scroll2="onScroll2" #default="props">
          <Instruction v-if="props.item.type=='instruction'" :address="props.item.address" :mnemonic="props.item.mnemonic" :op_str="props.item.op_str" :highlight="source.toInstructionHighlight(props.item.address,pc)" :breaking="source.toInstructionBreaking(props.item.address,breakpoints)" :group="instructionGroup" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></Instruction>
        </Scroller>
      </div>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
import Instruction from '@/views/Instruction';

function getRange(address) {
  const pieceOf = 147 * asmdb.getInstance().UNIT;
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
  constructor(pc, assembly) {
    for (var i = 0; i < assembly.length; i++) {
      if (assembly[i].type == 'instruction' && assembly[i].address >= pc) {
        break;
      }
    }
    for (var j = 0; i + j < assembly.length; j++) {
      this.append(j, assembly[i + j]);
    }
    for (var j = -1; i + j >= 0; j--) {
      this.append(j, assembly[i + j]);
    }
    var range = getRange(pc);
    this.pieceOf = 147 * asmdb.getInstance().UNIT;
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
      instruction: Instruction
    }[value.type].measureHeight(value);
    this[index] = value;
  }

  toInstructionHighlight(address, highlight) {
    return address == highlight;
  }

  toInstructionBreaking(address, breakpoints) {
    for (var breakpoint of breakpoints) {
      if (breakpoint.address == address) {
        if (breakpoint.disable) {
          return 2;
        }
        return 1;
      }
    }
    return 0;
  }

  getIndex(address) {
    for (var i = this.minIndex; i < this.maxIndex; i++) {
      if (this[i].type == 'instruction' && this[i].address == address) {
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

  onScroll(index) {
    var preLoad = 147;
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
      pc: null,
      source: null,
      breakpoints: [],
      counter: 0,
      hst: []
    };
  },
  computed: {
    windowWidth: function() {
      return 500;
    },
    instructionGroup: function() {
      return 6;
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
      this.$menu.alert(event, items, this.onClickMenu);
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
          //todo hstGet
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
    jumpTo: function(address) {
      //todo
    },
    smoothScrollBy: function(deltaY) {
      if (deltaY == 0) {
        return;
      }
      var duration = 147 + 224 * Math.min(Math.abs(deltaY) / screen.height, 1);
      var maxi = Math.ceil((duration * 3) / 50);
      var oldy = 0;
      var counter = this.counter;
      requestAnimationFrames(i => {
        if (counter != this.counter) {
          return true;
        }
        var value = ++i / maxi;
        var newy = parseInt(deltaY * value);
        if (oldy != newy) {
          this.$refs.scroller.scrollBy(newy - oldy);
        }
        oldy = newy;
        return !(i < maxi);
      });
    },
    getRange: function(pc) {
      if (this.source != null) {
        var index = this.source.getIndex(pc);
        if (index != null) {
          return null;
        }
      }
      return getRange(pc);
    },
    onBreak: function(pc, assembly) {
      this.disable = false;
      this.counter++;
      if (assembly != null) {
        this.source = new Source(pc, assembly);
      } else {
        var oldIndex = this.source.getIndex(this.pc);
        var oldOffset = oldIndex != null ? this.source.getOffset({ index: oldIndex, offset: 0 }) : null;
        var newIndex = this.source.getIndex(pc);
        var newOffset = newIndex != null ? this.source.getOffset({ index: newIndex, offset: 0 }) : null;
        var curOffset = this.source.getOffset(this.$refs.scroller.getPosition());
        var scrollType = 0;
        if (newOffset != null) {
          var maxOffset = this.$refs.scroller.$el.clientHeight;
          if (oldOffset != null && oldOffset - curOffset >= 0 && oldOffset - curOffset + this.source[oldIndex].height <= maxOffset) {
            scrollType = 1;
          } else {
            scrollType = 2;
          }
        }
        switch (scrollType) {
          case 1:
            this.smoothScrollBy(newOffset - oldOffset);
            break;
          case 2:
            this.smoothScrollBy(newOffset - curOffset);
            break;
        }
      }
      this.pc = pc;
    },
    onContinue: function() {
      this.disable = true;
    },
    onBreakpoints: function(breakpoints) {
      this.breakpoints = breakpoints;
    },
    onScroll2: function(position) {
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
