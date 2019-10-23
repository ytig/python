<template>
  <div class="bytes-container">
    <canvas ref="canvas"></canvas>
    <span v-for="(item, index) in items" :key="index" :class="item.style" v-html="item.value" @click="onClickItem(index)"></span>
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

function measureTextWidth(length) {
  return length * 7.224609375;
}

function measureTextHeight() {
  return 14;
}

function measureViewWidth(lineNumberLength, group, showString) {
  return Math.ceil(24 + measureTextWidth(lineNumberLength + 2 + 3 * group + parseInt(group / 8) - 2 + (showString ? 2 + group : 0)) + 2 * group);
}

function measureViewHeight() {
  return measureTextHeight() + 4;
}

function newItem(value, ...style) {
  return {
    value: value,
    style: style
  };
}

export default {
  measureWidth: measureViewWidth,
  measureHeight: measureViewHeight,
  data: function() {
    return {
      dirty: false,
      items: []
    };
  },
  props: {
    lineNumber: String,
    highlightNumber: Number,
    watchingNumbers: String,
    value: Object,
    group: Number,
    showString: Boolean,
    lazyLayout: Boolean
  },
  computed: {
    self: function() {
      return {
        lineNumber: this.lineNumber,
        highlightNumber: this.highlightNumber,
        watchingNumbers: this.watchingNumbers,
        value: this.value,
        group: this.group,
        showString: this.showString,
        lazyLayout: this.lazyLayout
      };
    }
  },
  watch: {
    self: function(newValue, oldValue) {
      var needLayout = false;
      var needDraw = false;
      if (newValue.lineNumber != oldValue.lineNumber || newValue.value != oldValue.value || newValue.group != oldValue.group || ewValue.showString != oldValue.showString) {
        needLayout = true;
        needDraw = true;
      }
      if (newValue.highlightNumber != oldValue.highlightNumber || newValue.watchingNumbers != oldValue.watchingNumbers) {
        needDraw = true;
      }
      if (!newValue.lazyLayout) {
        if (needLayout || this.dirty) {
          this.requestLayout();
          this.dirty = false;
        }
      } else {
        if (needLayout) {
          this.dirty = true;
        }
      }
      if (needDraw) {
        this.invalidate();
      }
    }
  },
  mounted: function() {
    this.requestLayout();
    this.invalidate();
  },
  methods: {
    requestLayout: function() {
      return; //for test
      var items = [];
      items.push(newItem(this.lineNumber));
      var event;
      for (var i = 0; i < this.group; i++) {
        if (i % groupBy() == 0) {
          items.push(newItem('&nbsp;'));
          if (i % 8 == 0) {
            items.push(newItem('&nbsp;'));
          }
          if (this.value == null) {
            event = null;
          } else if (i + groupBy() - 1 < this.value.newBytes.length) {
            var address = 0;
            for (var j = groupBy() - 1; j >= 0; j--) {
              address *= 256;
              address += this.value.newBytes.charCodeAt(i + j);
            }
            var usage = parseInt(usageOf(address)) - 2;
            if (usage >= 0) {
              event = [usage, address];
            } else {
              event = null;
            }
          } else {
            event = null;
          }
        } else {
          items.push(newItem('&nbsp;', event != null ? 'bytes-clickable' : ''));
          if (event != null) {
            items[items.length - 1].event = event;
          }
        }
        if (this.value == null) {
          items.push(newItem('00', 'bytes-padding'));
        } else {
          var charCode = '&nbsp;&nbsp;';
          if (i < this.value.newBytes.length) {
            var byte = this.value.newBytes.charCodeAt(i);
            charCode = byte.toString(16).zfill(2);
          }
          items.push(newItem(charCode, 'bytes-padding', event != null ? 'bytes-clickable' : ''));
          if (event != null) {
            items[items.length - 1].event = event;
          }
        }
      }
      this.items = items;
    },
    invalidate: function() {
      var cvs = this.$refs.canvas;
      var w = measureViewWidth(this.lineNumber.length, this.group, this.showString);
      var h = measureViewHeight();
      if (cvs.width != w || cvs.height != h) {
        cvs.width = w;
        cvs.height = h;
      }
      var cxt = cvs.getContext('2d');
      //todo
      cxt.fillText('test', 0, 14);
    },
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

.bytes-container {
  height: 18px;
  contain: strict;
  > canvas {
    position: absolute;
    pointer-events: none;
  }
  > span {
    line-height: 16px;
    font-size: 12px;
    color: transparent;
  }
  > span:first-of-type {
    margin-left: 12px;
  }
  .bytes-padding {
    padding-left: 1px;
    padding-right: 1px;
  }
  .bytes-clickable {
    cursor: pointer;
  }
}
</style>
