<template>
  <div class="bytes-container">
    <span v-for="(item, index) in items" :key="index" :class="item.style" v-html="item.value" @click="onClickItem(index)"></span>
  </div>
</template>

<script>
import Theme from '@/styles/theme';
import asmdb from '@/scripts/asmdb';

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
    canvasContext: String,
    lazyLayout: Boolean
  },
  computed: {
    self: function() {
      var highlightNumber = this.highlightNumber;
      if (highlightNumber != null) {
        if (highlightNumber < 0 || highlightNumber >= this.group) {
          highlightNumber = null;
        }
      }
      var watchingNumbers = [];
      for (var n of JSON.parse(this.watchingNumbers || '[]')) {
        if (n >= 0 && n < this.group) {
          watchingNumbers.push(n);
        }
      }
      watchingNumbers.sort();
      return {
        lineNumber: this.lineNumber,
        highlightNumber: highlightNumber,
        watchingNumbers: watchingNumbers,
        value: this.value,
        group: this.group,
        showString: this.showString,
        canvasContext: this.canvasContext,
        lazyLayout: this.lazyLayout
      };
    }
  },
  watch: {
    self: function(newValue, oldValue) {
      var needLayout = false;
      var needDraw = false;
      if (newValue.lineNumber != oldValue.lineNumber || newValue.value != oldValue.value || newValue.group != oldValue.group || newValue.showString != oldValue.showString) {
        needLayout = true;
        needDraw = true;
      }
      if (newValue.highlightNumber != oldValue.highlightNumber || JSON.stringify(newValue.watchingNumbers) != JSON.stringify(oldValue.watchingNumbers || newValue.canvasContext != oldValue.canvasContext)) {
        needDraw = true;
      }
      if (!newValue.lazyLayout) {
        if (needLayout || this.dirty) {
          this.layout();
          this.dirty = false;
        }
      } else {
        if (needLayout) {
          this.dirty = true;
        }
      }
      if (needDraw) {
        this.draw();
      }
    }
  },
  mounted: function() {
    this.layout();
    this.draw();
  },
  methods: {
    layout: function() {
      var self = this.self;
      var items = [];
      items.push(newItem(self.lineNumber));
      var event;
      for (var i = 0; i < self.group; i++) {
        if (i % 8 == 0) {
          items.push(newItem('&nbsp;'));
        }
        if (i % asmdb.asmUnit == 0) {
          items.push(newItem('&nbsp;'));
          if (self.value == null) {
            event = null;
          } else if (i + asmdb.asmUnit - 1 < self.value.newBytes.length) {
            var address = 0;
            for (var j = asmdb.asmUnit - 1; j >= 0; j--) {
              address *= 256;
              address += self.value.newBytes.charCodeAt(i + j);
            }
            var usage = parseInt(asmdb.getAddressUsage(address)) - 2;
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
        if (self.value == null) {
          items.push(newItem('00', 'bytes-padding'));
        } else {
          var charCode = '&nbsp;&nbsp;';
          if (i < self.value.newBytes.length) {
            var byte = self.value.newBytes.charCodeAt(i);
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
    draw: function() {
      var self = this.self;
      var cc = self.canvasContext.split(';');
      var h = measureViewHeight();
      var t = parseInt(cc[0]) * h;
      for (var i of cc[1].split(',')) {
        var c = getContext(parseInt(i), t, h);
        if (c != null) {
          this.draw_(c);
        }
      }
    },
    draw_: function(ctx) {
      var self = this.self;
      var w = measureViewWidth(self.lineNumber.length, self.group, self.showString);
      var h = measureViewHeight();
      ctx.clearRect(0, 0, w, h);
      if (self.highlightNumber != null) {
        ctx.fillStyle = Theme.colorBackgroundSelection;
        ctx.fillRect(0, 0, w, h - 2);
      }
      ctx.font = '12px Menlo';
      var x = 0;
      var y = 12;
      x += 12;
      ctx.fillStyle = self.highlightNumber == null ? Theme.colorTextDarker : Theme.colorTextDark;
      ctx.fillText(self.lineNumber, x, y);
      x += measureTextWidth(self.lineNumber.length);
      var coordinates = [];
      var usage;
      for (var i = 0; i < self.group; i++) {
        if (i % 8 == 0) {
          x += measureTextWidth(1);
        }
        if (i % asmdb.asmUnit == 0) {
          x += measureTextWidth(1);
          if (self.value == null) {
            usage = '0';
          } else if (i + asmdb.asmUnit - 1 < self.value.newBytes.length) {
            var address = 0;
            for (var j = asmdb.asmUnit - 1; j >= 0; j--) {
              address *= 256;
              address += self.value.newBytes.charCodeAt(i + j);
            }
            var usage = asmdb.getAddressUsage(address);
          } else {
            usage = '1';
          }
        } else {
          x += measureTextWidth(1);
        }
        var charCode = null;
        var changed = false;
        if (self.value == null) {
          charCode = '00';
        } else if (i < self.value.newBytes.length) {
          var byte = self.value.newBytes.charCodeAt(i);
          charCode = byte.toString(16).zfill(2);
          if (self.value.oldBytes != null && i < self.value.oldBytes.length) {
            if (byte != self.value.oldBytes.charCodeAt(i)) {
              changed = true;
            }
          }
        }
        var coordinate = {
          left: Math.round(x),
          right: Math.round(x) + Math.ceil(measureTextWidth(2)) + 2
        };
        coordinates.push(coordinate);
        x += 1;
        if (charCode != null) {
          switch (usage) {
            case '0':
              ctx.fillStyle = self.highlightNumber == null ? Theme.colorTextDarker : Theme.colorTextDark;
              break;
            case '1':
              ctx.fillStyle = Theme.colorText;
              break;
            case '2':
              ctx.fillStyle = Theme.colorText2;
              break;
            case '3':
              ctx.fillStyle = Theme.colorText3;
              break;
            case '4':
              ctx.fillStyle = Theme.colorText4;
              break;
          }
          if (changed) {
            ctx.fillRect(coordinate.left, 1, coordinate.right - coordinate.left, h - 4);
            ctx.fillStyle = Theme.colorBackground;
          }
          ctx.fillText(charCode, x, y);
          if (self.highlightNumber == i) {
            ctx.fillRect(coordinate.left + 1, h - 5, coordinate.right - coordinate.left - 2, 1);
          }
        }
        x += measureTextWidth(2) + 1;
      }
      ctx.fillStyle = Theme.colorIconBreakpoint;
      var s = 0;
      while (s < this.group) {
        if (self.watchingNumbers.indexOf(s) >= 0) {
          var e = s + 1;
          while (e < this.group) {
            if (self.watchingNumbers.indexOf(e) < 0) {
              break;
            }
            e++;
          }
          var x1 = coordinates[s].left - 3;
          var x2 = coordinates[e - 1].right + 3;
          var y1 = 0;
          var y2 = h - 2;
          ctx.fillRect(x1, y1, 1, y2 - y1);
          ctx.fillRect(x1, y1, x2 - x1, 1);
          ctx.fillRect(x2 - 1, y1, 1, y2 - y1);
          ctx.fillRect(x1, y2 - 1, x2 - x1, 1);
          s = e + 1;
        } else {
          s++;
        }
      }
      if (self.showString) {
        x += measureTextWidth(2);
        for (var i = 0; i < this.group; i++) {
          var charCode = null;
          if (self.value == null) {
            usage = '0';
            charCode = '.';
          } else if (i < self.value.newBytes.length) {
            var byte = self.value.newBytes.charCodeAt(i);
            if (byte >= 0x21 && byte <= 0x7e) {
              usage = '1';
              charCode = String.fromCharCode(byte);
            } else {
              usage = '0';
              charCode = '.';
            }
          }
          if (charCode != null) {
            switch (usage) {
              case '0':
                ctx.fillStyle = self.highlightNumber == null ? Theme.colorTextDarker : Theme.colorTextDark;
                break;
              case '1':
                ctx.fillStyle = Theme.colorText;
                break;
            }
            ctx.fillText(charCode, x, y);
          }
          x += measureTextWidth(1);
        }
      }
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
