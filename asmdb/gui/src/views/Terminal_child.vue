<template>
  <div class="terminal-child-container" v-html="value_"></div>
</template>

<script>
import Theme from '@/styles/theme';
import InfiniteMixin from './InfiniteMixin';
const WIDTH0 = 7;
const HEIGHT0 = 16;

function measureChar(char) {
  var width = 0;
  for (var i = 0; i < char.length; i++) {
    var charCode = char.charCodeAt(i); //todo
    if (charCode < 256) {
      width += WIDTH0;
    } else {
      window += 2 * WIDTH0;
    }
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
  return HEIGHT0 * Math.max(wrapstring(width, value).length, 1);
}

function newItem(value, ...style) {
  return {
    value: value,
    style: style
  };
}

export default {
  WIDTH0: WIDTH0,
  HEIGHT0: HEIGHT0,
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
      this.value_ = this.value; //todo padding?
    },
    onPreDraw: function() {
      return measureHeight(this.$el.clientWidth, this.value);
    },
    onDraw: function(ctx) {
      const PADDING0 = (HEIGHT0 - 14) / 2;
      var styles = JSON.parse(this.styles);
      ctx.font = '12px Menlo';
      var x = 0;
      var y = 0;
      var lines = wrapstring(this.$el.clientWidth, this.value);
      for (var line of lines) {
        for (var i = 0; i < line.length; i++) {
          var char = line.charAt(i);
          var width = measureChar(char);
          var style = {
            background: styles[i][1],
            color: styles[i][2]
          };
          if (style.background) {
            ctx.fillStyle = style.background;
            ctx.fillRect(x, y + PADDING0, width, 14);
          }
          if (style.color) {
            ctx.fillStyle = style.color;
          } else {
            ctx.fillStyle = !style.background ? Theme.colorText : Theme.colorBackground;
          }
          ctx.fillText(char, x, y + PADDING0 + 11);
          x += width;
        }
        x = 0;
        y += HEIGHT0;
      }
      if (this.cursor != null) {
        var cursor = JSON.parse(this.cursor);
        var N = parseInt(this.$el.clientWidth / 7);
        var row = parseInt(cursor[0] / N);
        var col = cursor[0] % N;
        var x1 = WIDTH0 * col;
        var x2 = x1 + WIDTH0;
        var y1 = HEIGHT0 * row + PADDING0;
        var y2 = y1 + 14;
        if (!cursor[1]) {
          ctx.fillStyle = Theme.colorText;
          ctx.fillRect(x1, y1, 1, y2 - y1);
          ctx.fillRect(x1, y1, x2 - x1, 1);
          ctx.fillRect(x2 - 1, y1, 1, y2 - y1);
          ctx.fillRect(x1, y2 - 1, x2 - x1, 1);
        } else {
          ctx.fillStyle = Theme.colorText;
          ctx.fillRect(x1, y1, x2 - x1, y2 - y1);
          if (row < lines.length) {
            ctx.save();
            ctx.beginPath();
            ctx.rect(x1, y1, x2 - x1, y2 - y1);
            ctx.clip();
            ctx.fillStyle = Theme.colorBackground;
            x = 0;
            y = HEIGHT0 * row;
            var line = lines[row];
            for (var i = 0; i < line.length; i++) {
              var char = line.charAt(i);
              ctx.fillText(char, x, y + PADDING0 + 11);
              x += measureChar(char);
            }
            ctx.restore();
          }
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
