<template>
  <div class="terminal-child-container">
    <span v-for="(item, index) in items" :key="index" :class="item.style" v-html="item.value"></span>
  </div>
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
      items: []
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
      var items = [];
      items.push(newItem(this.value));
      this.items.splice(0, this.items.length, ...items);
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
  height: 16px;
  > span {
    line-height: 16px;
    font-size: 12px;
    color: transparent;
    word-break: break-word;
  }
  > span:first-of-type {
    margin-left: 12px;
  }
}
</style>
