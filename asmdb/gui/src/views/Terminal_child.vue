<template>
  <div class="terminal-child-container" v-html="value_"></div>
</template>

<script>
import Theme from '@/styles/theme';
import InfiniteMixin from './InfiniteMixin';

function measureChar(char) {
  var width = 0;
  for (var i = 0; i < char.length; i++) {
    var charCode = char.charCodeAt(i);
    width += charCode < 256 ? 7 : 14; //todo
  }
  return width;
}

function wrapstring(width, value) {
  var strArr = [];
  while (value) {
    var index = 1;
    var width_ = measureChar(value.charAt(0));
    while (index < value.length) {
      width_ += measureChar(value.charAt(index));
      if (width_ > width) {
        break;
      }
      index++;
    }
    strArr.push(value.substring(0, index));
    value = value.substring(index);
  }
  return strArr;
}

function measureHeight(width, value) {
  return 16 * Math.max(wrapstring(width, value).length, 1);
}

function newItem(value, ...style) {
  return {
    value: value,
    style: style
  };
}

export default {
  measureChar: measureChar,
  measureHeight: measureHeight,
  mixins: [InfiniteMixin],
  data: function() {
    return {
      value_: ''
    };
  },
  props: {
    value: String,
    styles: String,
    cursor: String
  },
  created: function() {
    this.needLayout.push('value');
    this.needDraw.push('styles', 'cursor');
  },
  methods: {
    onLayout: function() {
      this.value_ = this.value;
    },
    onPreDraw: function() {
      return measureHeight(this.$el.clientWidth, this.value);
    },
    onDraw: function(ctx) {
      var styles = JSON.parse(this.styles);
      ctx.font = '12px Menlo';
      var x = 0;
      var y = 0;
      var style = { size: 0 };
      var lines = wrapstring(this.$el.clientWidth, this.value);
      for (var line of lines) {
        for (var i = 0; i < line.length; i++) {
          var char = line.charAt(i);
          var width = measureChar(char);
          while (!style.size) {
            style = {
              size: styles[0][0],
              background: styles[0][1],
              color: styles[0][2]
            };
            styles.splice(0, 1);
          }
          if (style.background) {
            ctx.fillStyle = style.background;
            ctx.fillRect(x, y + 1, width, 14);
          }
          if (style.color) {
            ctx.fillStyle = style.color;
          } else {
            ctx.fillStyle = !style.background ? Theme.colorText : Theme.colorBackground;
          }
          ctx.fillText(char, x, y + 12);
          x += width;
          style.size -= 1;
        }
        x = 0;
        y += 16;
      }
      if (this.cursor != null) {
        var cursor = JSON.parse(this.cursor);
        y = 0;
        var c = cursor[0];
        for (var line of lines) {
          if (c <= line.length) {
            var char = line.charAt(c);
            x = measureChar(line.substring(0, c));
            var w = measureChar(' ');
            ctx.fillStyle = Theme.colorText;
            var x1 = x;
            var x2 = x1 + w;
            var y1 = y + 1;
            var y2 = y1 + 14;
            if (!cursor[1]) {
              ctx.fillRect(x1, y1, 1, y2 - y1);
              ctx.fillRect(x1, y1, x2 - x1, 1);
              ctx.fillRect(x2 - 1, y1, 1, y2 - y1);
              ctx.fillRect(x1, y2 - 1, x2 - x1, 1);
            } else {
              ctx.fillRect(x1, y1, x2 - x1, y2 - y1);
              if (char) {
                ctx.save();
                ctx.rect(x1, y1, x2 - x1, y2 - y1);
                ctx.clip();
                ctx.fillStyle = Theme.colorBackground;
                ctx.fillText(char, x, y + 12);
                ctx.restore();
              }
            }
            break;
          }
          c -= line.length;
          y += 16;
        }
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.terminal-child-container {
  font-size: 12px;
  line-height: 16px;
  color: transparent;
  word-break: break-all;
  white-space: pre-wrap;
}
</style>
