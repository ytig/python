<template>
  <div class="registers-container" @wheel="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Navigation :name="'Registers'" :focus="focus" :disable="disable"></Navigation>
    <Empty v-if="empty" :text="'[no data]'" style="padding-top:12px;"></Empty>
    <Gird :style="{opacity:empty?0:1}" class="registers-gird" :column="4" :items="items" #default="props">
      <Register :value="props.item" @clickitem="onClickItem"></Register>
    </Gird>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
const asmType = 'arm32';

function regsOf() {
  switch (asmType) {
    case 'arm32':
      return ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15', 'r16'];
  }
}

export default {
  data: function() {
    var items = [];
    var lineFill = 0;
    for (var k of regsOf()) {
      if (k.length > lineFill) {
        lineFill = k.length;
      }
      items[items.length] = {
        lineName: k,
        oldValue: null,
        newValue: null
      };
    }
    for (var item of items) {
      item.lineFill = lineFill;
    }
    return {
      focus: false,
      disable: true,
      empty: true,
      items: items
    };
  },
  created: function() {
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
        this.$menu.close();
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
  padding-bottom: 2px;
  .registers-gird {
    padding-left: 12px;
  }
}
</style>
