<template>
  <div class="registers-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Navigation :name="'Registers'" :focus="focus" :disable="disable"></Navigation>
    <Empty class="registers-empty" v-if="empty" :text="'[no data]'"></Empty>
    <Gird class="registers-gird" :style="{opacity:empty?0:1}" :column="column" :items="items" #default="props">
      <Register :value="props.item" @clickitem="onClickItem"></Register>
    </Gird>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';

export default {
  data: function() {
    var column = 4;
    var items = [];
    var lineFills = [];
    var c = 0;
    for (var k of asmdb.REGS) {
      lineFills[c] = Math.max(k.length, lineFills[c] || 0);
      c = (c + 1) % column;
      items[items.length] = {
        lineName: k,
        oldValue: null,
        newValue: null
      };
    }
    c = 0;
    for (var item of items) {
      item.lineFill = lineFills[c];
      c = (c + 1) % column;
    }
    return {
      focus: false,
      disable: true,
      empty: true,
      column: column,
      items: items
    };
  },
  mounted: function() {
    keyboard.registerWindow(this);
    asmdb.registerEvent('registers', this);
  },
  destroyed: function() {
    asmdb.unregisterEvent('registers', this);
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
        this.$menu.alert(event);
      }
    },
    onKeyDown: function(event) {
      return false;
    },
    onBreak: function(registers) {
      this.disable = false;
      this.empty = false;
      for (var item of this.items) {
        item.oldValue = item.newValue;
        item.newValue = item.lineName in registers ? registers[item.lineName] : null;
      }
    },
    onContinue: function() {
      this.disable = true;
    },
    onClickItem: function(...args) {
      this.$emit('clickitem', ...args);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.registers-container {
  position: relative;
  padding-bottom: 2px;
  .registers-empty {
    position: absolute;
    top: 40px;
  }
  .registers-gird {
    padding-left: 12px;
  }
}
</style>
