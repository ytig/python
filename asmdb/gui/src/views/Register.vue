<template>
  <div class="register-container">
    <span>{{value.lineName}}</span>
    <span v-for="i in (value.lineFill+1-value.lineName.length)" :key="i" class="user-select-none">&nbsp;</span>
    <span :css-usage="cssUsage" :css-changed="cssChanged" @click="onClickItem">{{hexValue}}</span>
    <span class="user-select-none">&nbsp;</span>
    <span>{{strValue}}</span>
  </div>
</template>

<script>
const asmType = 'arm32';

function usageOf(val) {
  //todo
  if (val % 32 == 0) {
    return '2';
  }
  if (val % 32 == 1) {
    return '3';
  }
  if (val % 32 == 2) {
    return '4';
  }
  return '1';
}

function regsString(val) {
  var str = '';
  switch (usageOf(val)) {
    case '1':
      if (val >= 0x21 && val <= 0x7e) {
        if (val == 0x27) {
          str = '"\'"';
        } else {
          str = "'" + String.fromCharCode(val) + "'";
        }
      }
      break;
    case '3':
      str = 'sp+123'; //todo
      break;
  }
  return str;
}
function cpsrString(val) {
  var n = (val & 0x80000000) == 0 ? '' : 'N';
  var z = (val & 0x40000000) == 0 ? '' : 'Z';
  var c = (val & 0x20000000) == 0 ? '' : 'C';
  var v = (val & 0x10000000) == 0 ? '' : 'V';
  return n + z + c + v;
}

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
        case 'sp':
          return '';
        case 'cpsr':
          return cpsrString(this.value.newValue);
        default:
          return regsString(this.value.newValue);
      }
    },
    cssUsage: function() {
      if (this.value.newValue == null) {
        return '0';
      }
      switch (this.value.lineName) {
        case 'sp':
          return '3';
        case 'cpsr':
          return '1';
        default:
          return usageOf(this.value.newValue);
      }
    },
    cssChanged: function() {
      if (this.value.oldValue == null) {
        return false;
      }
      return this.value.oldValue != this.value.newValue;
    }
  },
  methods: {
    onClickItem: function() {
      var usage = parseInt(this.cssUsage) - 2;
      if (usage >= 0) {
        this.$emit('clickitem', usage, this.value.newValue);
      }
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
}
</style>
