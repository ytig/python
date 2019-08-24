<template>
  <div class="memory-container" :style="{width:windowWidth+'px'}" @mousedown="requestFocus">
    <Navigation :name="'Memory'" :focus="focus" :disable="disable"></Navigation>
    <Empty v-if="items.length==0" :text="'[no data]'" style="padding-top:12px;"></Empty>
    <div v-else>
      <Bytes :value="{lineNumber:'0x00112233',newBytes:[1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8],showString:true}"></Bytes>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard.js';
import asmdb from '@/scripts/asmdb.js';
const groupBy = 4; //4or8

function measureTextWidth(length) {
  return length * 7.224609375;
}

export default {
  data: function() {
    return {
      focus: false,
      disable: true,
      items: [],
      itemSelection: null,
      dict: {}
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
      return 24 + measureTextWidth(2 + (8 * groupBy) / 4 + 25 * this.column + 2 + 8 * this.column) + 16 * this.column;
    }
  },
  created: function() {
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
    },
    onKeyboardClick: function(event) {
      //todo
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme.less';

.memory-container {
}
</style>
