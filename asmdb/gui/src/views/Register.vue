<template>
  <div class="register-container">
    <span @mouseup="onMouseUpItem(-1, ...arguments)">{{value.lineName}}</span>
    <span v-for="i in (value.lineFill+1-value.lineName.length)" :key="i" class="user-select-none">&nbsp;</span>
    <span ref="bytes" :css-usage="cssUsage" :css-changed="cssChanged" :css-assigned="cssAssigned" @click="onClickItem(0)" @dblclick="onDoubleClickItem(0)" @mouseup="onMouseUpItem(0, ...arguments)">{{hexValue}}</span>
    <span class="user-select-none">&nbsp;</span>
    <span>{{strValue}}</span>
  </div>
</template>

<script>
import asmdb from '@/scripts/asmdb';

export default {
  props: {
    value: Object
  },
  computed: {
    hexValue: function() {
      if (this.value.newValue == null) {
        return '';
      }
      return '0x' + this.value.newValue.toString(16);
    },
    strValue: function() {
      if (this.value.newValue == null) {
        return '';
      }
      switch (this.value.lineName) {
        case 'cpsr':
          return asmdb.getInstance().getCpsrString(this.value.newValue);
        default:
          return asmdb.getInstance().getRegsString(this.value.newValue);
      }
    },
    cssUsage: function() {
      if (this.value.newValue == null) {
        return '0';
      }
      switch (this.value.lineName) {
        case 'cpsr':
          return '1';
        default:
          return asmdb.getInstance().getAddressUsage(this.value.newValue);
      }
    },
    cssChanged: function() {
      if (this.value.oldValue == null) {
        return false;
      }
      return this.value.oldValue != this.value.newValue;
    },
    cssAssigned: function() {
      return this.value.assigned;
    }
  },
  methods: {
    onClickItem: function(index) {
      var usage = parseInt(this.cssUsage) - 2;
      if (usage >= 0) {
        this.$emit('clickitem', usage, this.value.newValue);
      }
    },
    onDoubleClickItem: function(index) {
      var usage = parseInt(this.cssUsage) - 2;
      if (usage >= 0) {
        return;
      }
      var range = asmdb.getInstance().getRegistersRange();
      var inRange = range.indexOf(this.value.lineName) >= 0;
      if (asmdb.getInstance().isSuspend() && inRange) {
        var el = this.$refs.bytes;
        var rect = el.getBoundingClientRect();
        var placeholder = el.innerHTML.substring(2);
        this.$editor.alert(parseInt(rect.x + 2), parseInt(rect.y), 2 * asmdb.getInstance().UNIT, placeholder, this.onAssign.bind(this, this.value.lineName));
      }
    },
    onMouseUpItem: function(index, event) {
      if (event.button == 2) {
        var menu = this.onCreateMenu(index);
        this.$menu.alert(event, menu, i => {
          menu[i].event();
        });
        event.stopPropagation();
      }
    },
    onCreateMenu: function(index) {
      var items = [];
      if (index == -1) {
        var text = this.value.lineName;
        items.push(['Copy', '', true]);
        items[items.length - 1].event = () => {
          emptySelection();
          this.$toast.alert('Text Copied');
          copyText(text);
        };
      } else {
        var range = asmdb.getInstance().getRegistersRange();
        var inRange = range.indexOf(this.value.lineName) >= 0;
        var el = this.$refs.bytes;
        var rect = el.getBoundingClientRect();
        var text = el.innerHTML;
        var placeholder = text.substring(2);
        items.push(['Copy', '', true]);
        items[items.length - 1].event = () => {
          emptySelection();
          this.$toast.alert('Text Copied');
          copyText(text);
        };
        items.push(['Modify register', '', asmdb.getInstance().isSuspend() && inRange]);
        items[items.length - 1].event = () => {
          emptySelection();
          this.$editor.alert(parseInt(rect.x + 2), parseInt(rect.y), 2 * asmdb.getInstance().UNIT, placeholder, this.onAssign.bind(this, this.value.lineName));
        };
      }
      return items;
    },
    onAssign: function(name, value) {
      if (!asmdb.getInstance().isSuspend()) {
        return;
      }
      asmdb.getInstance().asgn('$' + name + '=' + value);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.register-container {
  padding-right: 12px;
  padding-bottom: 4px;
  display: flex;
  > span {
    font-size: 12px;
  }
  > span:first-child {
    color: @color-text;
  }
  > span:last-child {
    color: @color-text-dark;
    width: 0px;
    flex-grow: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
  > span[css-usage] {
    padding: 0px 2px;
  }
  > span[css-usage='1'] {
    color: @color-text;
  }
  > span[css-usage='1'][css-changed] {
    color: @color-background;
    background: @color-text;
  }
  > span[css-usage='2'] {
    cursor: pointer;
    color: @color-text2;
  }
  > span[css-usage='2'][css-changed] {
    color: @color-background;
    background: @color-text2;
  }
  > span[css-usage='3'] {
    cursor: pointer;
    color: @color-text3;
  }
  > span[css-usage='3'][css-changed] {
    color: @color-background;
    background: @color-text3;
  }
  > span[css-usage='4'] {
    cursor: pointer;
    color: @color-text4;
  }
  > span[css-usage='4'][css-changed] {
    color: @color-background;
    background: @color-text4;
  }
  > span[css-assigned] {
    color: @color-background !important;
    background: #ff0 !important;
  }
}
</style>
