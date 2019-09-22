<template>
  <div class="registers-container" @wheel="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Navigation :name="'Registers'" :focus="focus" :disable="disable"></Navigation>
    <Gird :column="4" :items="items" #default="props">
      <Register :name="props.item.name" :value="props.item.value" :fill="props.item.fill"></Register>
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
    var maxLen = 0;
    for (var k of regsOf()) {
      if (k.length > maxLen) {
        maxLen = k.length;
      }
      items[items.length] = {
        name: k,
        value: null
      };
    }
    for (var item of items) {
      item.fill = maxLen;
    }
    return {
      focus: false,
      disable: true,
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
      for (var item of this.items) {
        if (item.name in registers) {
          item.value = registers[item.name];
        }
      }
    },
    onContinue: function() {
      this.disable = true;
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.registers-container {
  padding-bottom: 2px;
}
</style>
