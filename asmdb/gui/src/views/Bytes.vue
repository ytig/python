<template>
  <div class="bytes-container">
    <span v-for="(item, index) in items" :key="index" :class="item.style" v-html="item.value" @click="onClickItem(index)" @dblclick="onDoubleClickItem(index)" @mouseup="onMouseUpItem(index, ...arguments)"></span>
  </div>
</template>

<script>
import Theme from '@/styles/theme';
import asmdb from '@/scripts/asmdb';
import InfiniteMixin from './InfiniteMixin';

function measureWidth(lineNumberLength, group, showString) {
  return Math.ceil(24 + measureLength(lineNumberLength + 2 + 3 * group + parseInt(group / 8) - 2 + (showString ? 2 + group : 0)) + 2 * group);
}

function measureHeight() {
  return 18;
}

function newItem(value, ...style) {
  return {
    value: value,
    style: style
  };
}

export default {
  measureWidth: measureWidth,
  measureHeight: measureHeight,
  mixins: [InfiniteMixin],
  data: function() {
    return {
      items: []
    };
  },
  props: {
    startAddress: Number,
    lineNumber: String,
    highlightNumber: Number,
    watchingNumbers: String,
    assignedNumbers: String,
    oldBytes: String,
    newBytes: String,
    group: Number,
    showString: Boolean
  },
  created: function() {
    this.needLayout.push('lineNumber', 'newBytes', 'group');
    this.needDraw.push('highlightNumber', 'watchingNumbers', 'assignedNumbers', 'oldBytes', 'showString');
  },
  methods: {
    onLayout: function() {
      var items = [];
      items.push(newItem(this.lineNumber));
      items[items.length - 1].index = -1;
      var event;
      for (var i = 0; i < this.group; i++) {
        if (i % 8 == 0) {
          items.push(newItem('&nbsp;'));
        }
        if (i % asmdb.getInstance().UNIT == 0) {
          items.push(newItem('&nbsp;'));
          items[items.length - 1].index = i;
          if (this.newBytes == null) {
            event = null;
          } else if (i + asmdb.getInstance().UNIT - 1 < this.newBytes.length) {
            var address = 0;
            for (var j = asmdb.getInstance().UNIT - 1; j >= 0; j--) {
              address *= 256;
              address += this.newBytes.charCodeAt(i + j);
            }
            var usage = parseInt(asmdb.getInstance().getAddressUsage(address)) - 2;
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
          items[items.length - 1].index = i;
        }
        if (this.newBytes == null) {
          items.push(newItem('00', 'bytes-padding'));
          items[items.length - 1].index = i;
        } else {
          var charCode = '&nbsp;&nbsp;';
          if (i < this.newBytes.length) {
            var byte = this.newBytes.charCodeAt(i);
            charCode = byte.toString(16).zfill(2);
          }
          items.push(newItem(charCode, 'bytes-padding', event != null ? 'bytes-clickable' : ''));
          if (event != null) {
            items[items.length - 1].event = event;
          }
          items[items.length - 1].index = i;
        }
      }
      this.items.splice(0, this.items.length, ...items);
    },
    onPreDraw: function() {
      return measureHeight();
    },
    onDraw: function(ctx) {
      var watchingNumbers = JSON.parse(this.watchingNumbers);
      var assignedNumbers = JSON.parse(this.assignedNumbers);
      var w = measureWidth(this.lineNumber.length, this.group, this.showString);
      var h = measureHeight();
      if (this.highlightNumber != null) {
        ctx.fillStyle = Theme.colorBackgroundSelection;
        ctx.fillRect(0, 0, w, h - 2);
      }
      ctx.font = '12px Menlo';
      var x = 0;
      var y = 12;
      x += 12;
      ctx.fillStyle = this.highlightNumber == null ? Theme.colorTextDarker : Theme.colorTextDark;
      ctx.fillText(this.lineNumber, x, y);
      x += measureLength(this.lineNumber.length);
      var coordinates = [];
      var usage;
      for (var i = 0; i < this.group; i++) {
        if (i % 8 == 0) {
          x += measureLength(1);
        }
        if (i % asmdb.getInstance().UNIT == 0) {
          x += measureLength(1);
          if (this.newBytes == null) {
            usage = '0';
          } else if (i + asmdb.getInstance().UNIT - 1 < this.newBytes.length) {
            var address = 0;
            for (var j = asmdb.getInstance().UNIT - 1; j >= 0; j--) {
              address *= 256;
              address += this.newBytes.charCodeAt(i + j);
            }
            var usage = asmdb.getInstance().getAddressUsage(address);
          } else {
            usage = '1';
          }
        } else {
          x += measureLength(1);
        }
        var charCode = null;
        var changed = false;
        if (this.newBytes == null) {
          charCode = '00';
        } else if (i < this.newBytes.length) {
          var byte = this.newBytes.charCodeAt(i);
          charCode = byte.toString(16).zfill(2);
          if (this.oldBytes != null && i < this.oldBytes.length) {
            if (byte != this.oldBytes.charCodeAt(i)) {
              changed = true;
            }
          }
        }
        var coordinate = {
          left: Math.round(x),
          right: Math.round(x) + Math.ceil(measureLength(2)) + 2
        };
        coordinates.push(coordinate);
        x += 1;
        if (charCode != null) {
          switch (usage) {
            case '0':
              ctx.fillStyle = this.highlightNumber == null ? Theme.colorTextDarker : Theme.colorTextDark;
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
          if (assignedNumbers.indexOf(i) >= 0) {
            ctx.fillStyle = '#ff0';
            changed = true;
          }
          if (changed) {
            ctx.fillRect(coordinate.left, 1, coordinate.right - coordinate.left, h - 4);
            ctx.fillStyle = Theme.colorBackground;
          }
          ctx.fillText(charCode, x, y);
          if (this.highlightNumber == i) {
            ctx.fillRect(coordinate.left + 1, h - 5, coordinate.right - coordinate.left - 2, 1);
          }
        }
        x += measureLength(2) + 1;
      }
      ctx.fillStyle = Theme.colorIconBreakpoint;
      var s = 0;
      while (s < this.group) {
        if (watchingNumbers.indexOf(s) >= 0) {
          var e = s + 1;
          while (e < this.group) {
            if (watchingNumbers.indexOf(e) < 0) {
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
      if (this.showString) {
        x += measureLength(2);
        for (var i = 0; i < this.group; i++) {
          var charCode = null;
          if (this.newBytes == null) {
            usage = '0';
            charCode = '.';
          } else if (i < this.newBytes.length) {
            var byte = this.newBytes.charCodeAt(i);
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
                ctx.fillStyle = this.highlightNumber == null ? Theme.colorTextDarker : Theme.colorTextDark;
                break;
              case '1':
                ctx.fillStyle = Theme.colorText;
                break;
            }
            ctx.fillText(charCode, x, y);
          }
          x += measureLength(1);
        }
      }
    },
    onClickItem: function(index) {
      if (this.items[index] && this.items[index].event) {
        this.$emit('clickitem', ...this.items[index].event);
      }
    },
    onDoubleClickItem: function(index) {
      if (this.items[index] && this.items[index].event) {
        return;
      }
      if (this.items[index] && this.items[index].index != undefined) {
        if (this.items[index].index == -1) {
        } else {
          var address = this.startAddress + this.items[index].index;
          var range = asmdb.getInstance().getMemoryRange();
          var inRange = address >= range[0] && address < range[1];
          if (asmdb.getInstance().isSuspend() && inRange) {
            var el = this.$el.getElementsByClassName('bytes-padding')[this.items[index].index];
            var rect = el.getBoundingClientRect();
            var placeholder = el.innerHTML;
            this.$editor.alert(parseInt(rect.x + 1 - measureLength(2)), parseInt(rect.y), 2, placeholder, this.onAssign.bind(this, address));
          }
        }
      }
    },
    onMouseUpItem: function(index, event) {
      if (event.button == 2) {
        if (this.items[index] && this.items[index].index != undefined) {
          var anchor, focus;
          if (this.items[index].index == -1) {
            anchor = 0;
            focus = 1;
          } else {
            var floor = this.items[index].index - (this.items[index].index % asmdb.getInstance().UNIT);
            anchor = 0;
            while (this.items[anchor].index == undefined || this.items[anchor].index < floor) {
              anchor++;
            }
            focus = anchor + 2 * asmdb.getInstance().UNIT;
          }
          var selection = getSelection();
          selection.collapse(this.$el, anchor);
          selection.extend(this.$el, focus);
          var menu = this.onCreateMenu(this.items[index].index);
          this.$menu.alert(event, menu, i => {
            menu[i].event();
          });
          event.stopPropagation();
        }
      }
    },
    onCreateMenu: function(index) {
      var items = [];
      if (index == -1) {
        var text = this.lineNumber;
        items.push(['Copy', '', true]);
        items[items.length - 1].event = () => {
          emptySelection();
          this.$toast.alert('Text Copied');
          copyText(text);
        };
      } else {
        var address = this.startAddress + index;
        var range = asmdb.getInstance().getMemoryRange();
        var inRange = address >= range[0] && address < range[1];
        var intValue = 0;
        var i = index - (index % asmdb.getInstance().UNIT);
        if (!asmdb.getInstance().BEND) {
          for (var j = asmdb.getInstance().UNIT - 1; j >= 0; j--) {
            intValue *= 256;
            intValue += (this.newBytes || '').charCodeAt(i + j) || 0;
          }
        } else {
          for (var j = 0; j < asmdb.getInstance().UNIT; j++) {
            intValue *= 256;
            intValue += (this.newBytes || '').charCodeAt(i + j) || 0;
          }
        }
        items.push(['Copy', '', true]);
        items[items.length - 1].event = () => {
          emptySelection();
          this.$toast.alert('Text Copied');
          copyText('0x' + intValue.toString(16));
        };
        var watching = JSON.parse(this.watchingNumbers).indexOf(index) >= 0;
        var canWatch = asmdb.getInstance().getWatchpointsLength() < asmdb.getInstance().WLEN && inRange;
        items.push([!watching ? 'Watching' : 'Watching done', '', watching || canWatch]);
        items[items.length - 1].event = () => {
          emptySelection();
          var addr = address - (address % asmdb.getInstance().UNIT);
          if (!watching) {
            asmdb.getInstance().wpt([], [{ address: addr }]);
          } else {
            asmdb.getInstance().wpt([{ address: addr }], []);
          }
        };
        var el = this.$el.getElementsByClassName('bytes-padding')[index];
        var rect = el.getBoundingClientRect();
        var placeholder = el.innerHTML;
        items.push(['Modify memory', '', asmdb.getInstance().isSuspend() && inRange]);
        items[items.length - 1].event = () => {
          emptySelection();
          this.$editor.alert(parseInt(rect.x + 1 - measureLength(2)), parseInt(rect.y), 2, placeholder, this.onAssign.bind(this, address));
        };
      }
      return items;
    },
    onAssign: function(address, value) {
      if (!asmdb.getInstance().isSuspend()) {
        return;
      }
      asmdb.getInstance().asgn('*' + address + '=' + value);
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
