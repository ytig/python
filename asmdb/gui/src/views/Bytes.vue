<template>
  <div class="bytes-container" :highlight="highlight">
    <span v-for="(item, index) in items" :key="index" :class="item.style" v-html="item.value" @mousedown="onClickItem($event, index)"></span>
  </div>
</template>

<script>
const groupBy = 4; //4or8

function usageOf(int) {
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
  data: function() {
    return {
      highlight: false,
      items: []
    };
  },
  props: {
    value: Object
  },
  watch: {
    value: 'invalidate'
  },
  created: function() {
    this.invalidate();
  },
  methods: {
    onClickItem: function(event, index) {
      switch (event.button) {
        case 0:
          if (this.items[index] && this.items[index].event) {
            this.$emit('clickitem', ...this.items[index].event);
          }
          break;
        case 2:
          console.log('todo');
          break;
      }
    },
    invalidate: function() {
      this.highlight = typeof this.value.highlightNumber == 'number';
      var items = [];
      //line number
      items[items.length] = {
        value: this.value.lineNumber,
        style: 'bytes-line-number' + (this.highlight ? ' bytes-highlight' : '')
      };
      //hex
      var curInt;
      var curUsage;
      for (var i = 0; i < this.value.newBytes.length; i++) {
        if (i % groupBy == 0) {
          items[items.length] = {
            value: '&nbsp;',
            style: 'bytes-space'
          };
          if (i % 8 == 0) {
            items[items.length] = {
              value: '&nbsp;',
              style: 'bytes-space'
            };
          }
          if (i + groupBy - 1 < this.value.newBytes.length) {
            curInt = 0;
            for (var j = groupBy - 1; j >= 0; j--) {
              curInt *= 256;
              curInt += this.value.newBytes[i + j];
            }
            curUsage = usageOf(curInt);
          } else {
            curInt = null;
            curUsage = '1';
          }
        } else {
          items[items.length] = {
            value: '&nbsp;',
            style: 'bytes-space bytes-usage-' + curUsage
          };
          if (curUsage != '1') {
            items[items.length - 1].event = [parseInt(curUsage) - 2, curInt];
          }
        }
        var isChanged = false;
        if (Boolean(this.value.oldBytes) && i < this.value.oldBytes.length) {
          isChanged = this.value.oldBytes[i] != this.value.newBytes[i];
        }
        items[items.length] = {
          value: this.value.newBytes[i].toString(16).zfill(2),
          style: 'bytes-hex bytes-usage-' + curUsage + ' bytes-changed-' + isChanged + (this.value.highlightNumber == i ? ' bytes-highlight' : '')
        };
        if (curUsage != '1') {
          items[items.length - 1].event = [parseInt(curUsage) - 2, curInt];
        }
      }
      //string
      if (this.value.showString) {
        items[items.length] = {
          value: '&nbsp;',
          style: 'bytes-space user-select-none'
        };
        items[items.length] = {
          value: '&nbsp;',
          style: 'bytes-space user-select-none'
        };
        for (var i = 0; i < this.value.newBytes.length; i++) {
          var byte = this.value.newBytes[i];
          if (byte >= 0x21 && byte <= 0x7e) {
            items[items.length] = {
              value: String.fromCharCode(byte),
              style: 'bytes-string user-select-none bytes-visible-' + true
            };
          } else {
            items[items.length] = {
              value: '.',
              style: 'bytes-string user-select-none bytes-visible-' + false
            };
          }
        }
      }
      //padding
      items.splice(0, 0, { value: '', style: '' });
      items.splice(items.length, 0, { value: '', style: '' });
      this.items.splice(0, this.items.length, ...items);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme.less';

.bytes-container[highlight='true'] {
  > * {
    background: @color-selection-background;
  }
}
.bytes-container {
  white-space: nowrap;
  margin-bottom: 4px;
  > span {
    font-size: 12px;
  }
  > span:first-child {
    padding-left: 12px;
  }
  > span:last-child {
    padding-right: 12px;
  }

  .bytes-line-number {
    color: @color-darker-text;
  }
  .bytes-line-number.bytes-highlight {
    color: @color-dark-text;
  }

  .bytes-hex {
    padding: 0px 1px;
  }
  .bytes-hex.bytes-highlight {
    text-decoration: underline;
  }
  .bytes-hex.bytes-usage-1.bytes-changed-false {
    color: @color-text;
  }
  .bytes-hex.bytes-usage-1.bytes-changed-true {
    color: @color-background;
    background: @color-text !important;
  }
  .bytes-usage-2 {
    cursor: pointer;
  }
  .bytes-hex.bytes-usage-2.bytes-changed-false {
    color: @color-text2;
  }
  .bytes-hex.bytes-usage-2.bytes-changed-true {
    color: @color-background;
    background: @color-text2 !important;
  }
  .bytes-usage-3 {
    cursor: pointer;
  }
  .bytes-hex.bytes-usage-3.bytes-changed-false {
    color: @color-text3;
  }
  .bytes-hex.bytes-usage-3.bytes-changed-true {
    color: @color-background;
    background: @color-text3 !important;
  }
  .bytes-usage-4 {
    cursor: pointer;
  }
  .bytes-hex.bytes-usage-4.bytes-changed-false {
    color: @color-text4;
  }
  .bytes-hex.bytes-usage-4.bytes-changed-true {
    color: @color-background;
    background: @color-text4 !important;
  }

  .bytes-string.bytes-visible-true {
    color: @color-text;
  }
  .bytes-string.bytes-visible-false {
    color: @color-darker-text;
  }
}
</style>
