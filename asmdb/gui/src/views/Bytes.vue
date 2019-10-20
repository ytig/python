<template>
  <div class="bytes-container" :css-highlight="highlight">
    <span></span>
    <span v-for="(item, index) in items" :key="index" :class="item.style" v-html="item.value" @click="onClickItem(index)"></span>
    <span></span>
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

function newItem(value, ...style) {
  return {
    value: value,
    style: style
  };
}

export default {
  props: {
    lineNumber: String,
    highlightNumber: Number,
    watchingNumbers: String,
    value: Object,
    group: Number,
    showString: Boolean
  },
  computed: {
    highlight: function() {
      return this.highlightNumber != null && this.value != null && this.highlightNumber >= 0 && this.highlightNumber < this.value.newBytes.length;
    },
    items: function() {
      var highlight = null;
      if (this.highlightNumber != null && this.value != null && this.highlightNumber >= 0 && this.highlightNumber < this.value.newBytes.length) {
        highlight = this.highlightNumber;
      }
      var watching = JSON.parse(this.watchingNumbers || '[]');
      var items = [];
      //line number
      items.push(newItem(this.lineNumber, 'bytes-line-number', highlight != null ? 'bytes-highlight' : ''));
      //hex
      var curUsage;
      var curEvent;
      var bordering = false;
      for (var i = 0; i < this.group; i++) {
        if (i % groupBy() == 0) {
          items.push(newItem('&nbsp;', 'bytes-space', bordering ? 'bytes-border-top bytes-border-bottom' : ''));
          if (i % 8 == 0) {
            items.push(newItem('&nbsp;', 'bytes-space', bordering ? 'bytes-border-top bytes-border-bottom' : ''));
          }
          if (this.value == null) {
            curUsage = '0';
            curEvent = null;
          } else if (i + groupBy() - 1 < this.value.newBytes.length) {
            var curAddress = 0;
            for (var j = groupBy() - 1; j >= 0; j--) {
              curAddress *= 256;
              curAddress += this.value.newBytes.charCodeAt(i + j);
            }
            curUsage = usageOf(curAddress);
            var curUsage2 = parseInt(curUsage) - 2;
            if (curUsage2 >= 0) {
              curEvent = [curUsage2, curAddress];
            } else {
              curEvent = null;
            }
          } else {
            curUsage = '1';
            curEvent = null;
          }
        } else {
          items.push(newItem('&nbsp;', 'bytes-space', 'bytes-usage-' + curUsage, bordering ? 'bytes-border-top bytes-border-bottom' : ''));
          if (curEvent != null) {
            items[items.length - 1].event = curEvent;
          }
        }
        if (this.value == null) {
          items.push(newItem('00', 'bytes-hex', 'bytes-usage-' + curUsage));
        } else {
          var charCode = '&nbsp;&nbsp;';
          var isChanged = false;
          if (i < this.value.newBytes.length) {
            var byte = this.value.newBytes.charCodeAt(i);
            charCode = byte.toString(16).zfill(2);
            if (Boolean(this.value.oldBytes) && i < this.value.oldBytes.length) {
              isChanged = this.value.oldBytes[i] != this.value.newBytes[i];
            }
          }
          items.push(newItem(charCode, 'bytes-hex', 'bytes-usage-' + curUsage, 'bytes-changed-' + isChanged, highlight == i ? 'bytes-highlight' : ''));
          if (watching.indexOf(i) >= 0) {
            items[items.length - 1].style.push('bytes-border-top bytes-border-bottom');
            if (watching.indexOf(i - 1) < 0) {
              items[items.length - 1].style.push('bytes-border-left');
              bordering = true;
            }
            if (watching.indexOf(i + 1) < 0) {
              items[items.length - 1].style.push('bytes-border-right');
              bordering = false;
            }
          }
          if (curEvent != null) {
            items[items.length - 1].event = curEvent;
          }
        }
      }
      //string
      if (this.showString) {
        items.push(newItem('&nbsp;', 'bytes-space', 'user-select-none'));
        items.push(newItem('&nbsp;', 'bytes-space', 'user-select-none'));
        if (this.value == null) {
          for (var i = 0; i < this.group; i++) {
            items.push(newItem('.', 'bytes-string', 'bytes-visible-' + false, 'user-select-none'));
          }
        } else {
          for (var i = 0; i < this.value.newBytes.length; i++) {
            var byte = this.value.newBytes.charCodeAt(i);
            if (byte >= 0x21 && byte <= 0x7e) {
              items.push(newItem(String.fromCharCode(byte), 'bytes-string', 'bytes-visible-' + true, 'user-select-none'));
            } else {
              items.push(newItem('.', 'bytes-string', 'bytes-visible-' + false, 'user-select-none'));
            }
          }
        }
      }
      return items;
    }
  },
  methods: {
    onClickItem: function(index) {
      if (this.items[index] && this.items[index].event) {
        this.$emit('clickitem', ...this.items[index].event);
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.bytes-container[css-highlight] {
  > * {
    background: @color-background-selection;
  }
}
.bytes-container {
  white-space: nowrap;
  padding-top: 1px;
  padding-bottom: 3px;
  > span {
    font-size: 12px;
  }
  > span:first-child {
    padding-left: 12px;
  }
  > span:last-child {
    padding-right: 12px;
  }

  .bytes-border-top {
    border-top: 1px solid @color-icon-breakpoint;
  }
  .bytes-border-bottom {
    border-bottom: 1px solid @color-icon-breakpoint;
  }

  .bytes-line-number {
    color: @color-text-darker;
  }
  .bytes-line-number.bytes-highlight {
    color: @color-text-dark;
  }

  .bytes-hex {
    padding: 0px 1px;
  }
  .bytes-hex.bytes-border-left {
    margin-left: -1px;
    border-left: 1px solid @color-icon-breakpoint;
  }
  .bytes-hex.bytes-border-right {
    margin-right: -1px;
    border-right: 1px solid @color-icon-breakpoint;
  }
  .bytes-hex.bytes-highlight {
    text-decoration: underline;
  }
  .bytes-hex.bytes-usage-0 {
    color: @color-text-darker;
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
    color: @color-text-darker;
  }
}
</style>
