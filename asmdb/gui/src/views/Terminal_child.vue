<template>
  <div class="terminal-child-container">{{value_}}</div>
</template>

<script>
import Theme from '@/styles/theme';
import InfiniteMixin from './InfiniteMixin';

function measureHeight(width, value) {
  return 16; //todo wrap
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
      return measureHeight(this.$el.clientWidth, this.value);
    },
    onDraw: function(ctx) {
      ctx.font = '12px Menlo';
      ctx.fillStyle = Theme.colorText;
      ctx.fillText(this.value, 12, 12);
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
