<template>
  <div class="registers-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Navigation :name="'Registers'" :focus="focus" :disable="disable" @mouseup2="onMouseUp2"></Navigation>
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
    for (var k of asmdb.getInstance().REGS) {
      lineFills[c] = Math.max(k.length, lineFills[c] || 0);
      c = (c + 1) % column;
      items.push({
        lineName: k,
        oldValue: null,
        newValue: null,
        assigned: false
      });
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
    asmdb.getInstance().registerEvent('registers', this);
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('registers', this);
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
        this.$menu.close();
      }
    },
    onMouseUp2: function(evnet) {
      this.$menu.alert(event);
    },
    onKeyDown: function(event) {
      return false;
    },
    onBreak: function(registers) {
      this.disable = false;
      this.empty = false;
      var items = [];
      for (var item of this.items) {
        item = Object.assign({}, item);
        item.oldValue = item.newValue;
        item.newValue = item.lineName in registers ? registers[item.lineName] : null;
        item.assigned = false;
        items.push(item);
      }
      this.items.splice(0, this.items.length, ...items);
    },
    onContinue: function() {
      this.disable = true;
    },
    onAssigned: function(name, value) {
      for (var item of this.items) {
        if (item.lineName == name) {
          item.newValue = value;
          item.assigned = true;
        }
      }
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
  padding-bottom: 2px;
  .registers-gird {
    padding-left: 12px;
  }
}
</style>
