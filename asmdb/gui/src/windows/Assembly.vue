<template>
  <div class="assembly-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" :theme="0" :condition="searchTest" @search="jumpTo"></Search>
    <Navigation :name="'Assembly'" :focus="focus" :disable="disable" :gradient="true" @mouseup2="onMouseUp2"></Navigation>
    <div class="assembly-column">
      <div class="assembly-row">
        <Scroller v-if="source!=null" ref="scroller" class="assembly-scroller" :style="{width:windowWidth+'px'}" :source="source" @scroll2="onScroll2" #default="props">
          <Instruction :address="props.item.address" :mnemonic="props.item.mnemonic" :op_str="props.item.op_str" :highlight="props.item.highlight" :breaking="props.item.breaking" :group="instructionGroup" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></Instruction>
        </Scroller>
      </div>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';

class Source {
  constructor() {
    //todo
  }
}

export default {
  data: function() {
    return {
      focus: false,
      disable: true,
      source: null,
      breakpoints: [],
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
    getRange: function(pc) {
      //todo
      return null;
    },
    onBreak: function(pc, assembly) {
      this.disable = false;
      //todo
    },
    onContinue: function() {
      this.disable = true;
    },
    onBreakpoints: function(breakpoints) {
      this.breakpoints = breakpoints;
    },
    onScroll2: function(position) {
      //todo
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
