<template>
  <div class="terminal-child-container" v-html="value_"></div>
</template>

<script>
import Theme from '@/styles/theme';
import InfiniteMixin from './InfiniteMixin';

function wrapstring(width, value) {
  var strArr = [];
  while (value) {
    var index = value.length;
    while (measureText(value.substring(0, index)) > width) {
      if (index == value.length) {
        var limit = parseInt(width / 7);
        if (measureText(value.substring(0, limit)) > width) {
          index = Math.min(index, limit);
        }
      }
      index--;
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
        x = 0;
        while (line) {
          while (!style.size) {
            style = {
              size: styles[0][0],
              background: styles[0][1],
              color: styles[0][2]
            };
            styles.splice(0, 1);
          }
          var len = Math.min(line.length, style.size);
          var text = line.substring(0, len);
          var width = measureText(text);
          if (style.background) {
            ctx.fillStyle = style.background;
            ctx.fillRect(x, y + 1, width, 14);
          }
          if (style.color) {
            ctx.fillStyle = style.color;
          } else {
            ctx.fillStyle = !style.background ? Theme.colorText : Theme.colorBackground;
          }
          ctx.fillText(text, x, y + 12);
          x += width;
          line = line.substring(len);
          style.size -= len;
        }
        y += 16;
      }
      if (this.cursor != null) {
        var cursor = JSON.parse(this.cursor);
        y = 0;
        var c = cursor[0];
        for (var line of lines) {
          if (c <= line.length) {
            var word = line.substring(c, c + 1);
            x = measureText(line.substring(0, c));
            var w = measureText(' ');
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
              if (word) {
                ctx.save();
                ctx.rect(x1, y1, x2 - x1, y2 - y1);
                ctx.clip();
                ctx.fillStyle = Theme.colorBackground;
                ctx.fillText(word, x, y + 12);
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
