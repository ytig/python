<template>
  <div class="register-container">
    <span class="user-select-none">{{value.lineName}}</span>
    <span v-for="i in (value.lineFill+1-value.lineName.length)" :key="i" class="user-select-none">&nbsp;</span>
    <span :css-usage="cssUsage" :css-changed="cssChanged" @click="onClickItem">{{hexValue}}</span>
    <span>&nbsp;</span>
    <span>{{strValue}}</span>
  </div>
</template>

<script>
const asmType = 'arm32';

function groupBy() {
  switch (asmType) {
    case 'arm32':
      return 4;
  }
}

function usageOf(int) {
  if (int % 32 == 0) {
    return '2';
  }
  if (int % 32 == 1) {
    return '3';
  }
  if (int % 32 == 2) {
    return '4';
  }
  //todo check?
  if (int >= 0x08048000 && int <= 0x08049000) {
    return '2';
  }
  if (int >= 0xbfcb4000 && int <= 0xbfcc9000) {
    return '3';
  }
  if (int >= 0x08ac5000 && int <= 0x08ae6000) {
    return '4';
  }
  if (int >= 0x08049000 && int <= 0x0804a000) {
    return '4';
  }
  return '1';
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
      return '0x' + this.value.newValue.toString(16).zfill(2 * groupBy());
    },
    strValue: function() {
      if (this.value.newValue == null) {
        return '';
      }
      var val = this.value.newValue;
      var str = '';
      switch (usageOf(val)) {
        case '1':
          if (val >= 0x21 && val <= 0x7e) {
            if (val == 0x27) {
              str = "'\\''";
            } else {
              str = "'" + String.fromCharCode(val) + "'";
            }
          }
          break;
        case '3': //todo
          str = 'sp+123';
          break;
      }
      return str;
    },
    cssUsage: function() {
      if (this.value.newValue == null) {
        return '0';
      }
      return usageOf(this.value.newValue);
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
    color: @color-text-darker;
  }
  > span:last-child {
    color: @color-text-darker;
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
