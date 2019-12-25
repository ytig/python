<template>
  <div class="terminal-child-container">{{value_}}</div>
</template>

<script>
import Theme from '@/styles/theme';
import InfiniteMixin from './InfiniteMixin';

function wrapstring(width, value) {
  var strArr = [];
  while (value) {
    var index = 1;
    while (index < value.length && measureText(value.substring(0, index + 1)) < width) {
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
  measureHeight: measureHeight,
  mixins: [InfiniteMixin],
  data: function() {
    return {
      value_: ''
    };
  },
  props: {
    focus: Boolean,
    cursor: Number,
    value: String
  },
  created: function() {
    this.needLayout.push('value');
    this.needDraw.push('focus', 'cursor');
  },
  methods: {
    onLayout: function() {
      this.value_ = this.value;
    },
    onPreDraw: function() {
      return measureHeight(this.$el.clientWidth - 24, this.value);
    },
    onDraw: function(ctx) {
      ctx.font = '12px Menlo';
      var x = 0;
      var y = 12;
      x += 12;
      ctx.fillStyle = Theme.colorText;
      for (var line of wrapstring(this.$el.clientWidth - 24, this.value)) {
        ctx.fillText(line, x, y);
        y += 16;
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.terminal-child-container {
  padding-left: 12px;
  padding-right: 12px;
  font-size: 12px;
  line-height: 16px;
  color: transparent;
  word-break: break-all;
  white-space: pre-wrap;
}
</style>
