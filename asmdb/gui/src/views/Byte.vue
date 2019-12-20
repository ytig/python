<template>
  <div class="byte-container">
    <span v-for="(item, index) in items" :key="index" :class="item.style" v-html="item.value"></span>
  </div>
</template>

<script>
import Theme from '@/styles/theme';
import asmdb from '@/scripts/asmdb';
import InfiniteMixin from './InfiniteMixin';

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
  measureHeight: measureHeight,
  mixins: [InfiniteMixin],
  data: function() {
    return {
      items: []
    };
  },
  props: {
    address: Number,
    value: Number,
    highlight: Boolean,
    running: Boolean
  },
  created: function() {
    this.needLayout.push('address', 'value');
    this.needDraw.push('highlight', 'running');
  },
  methods: {
    onLayout: function() {
      var items = [];
      var address = '0x' + this.address.toString(16).zfill(2 * asmdb.getInstance().UNIT);
      items.push(newItem(address));
      items.push(newItem('&nbsp;'));
      items.push(newItem('&nbsp;'));
      items.push(newItem(this.value.toString(16).zfill(2)));
      if (this.value >= 0x21 && this.value <= 0x7e) {
        items.push(newItem('&nbsp;'));
        var charCode = String.fromCharCode(this.value);
        items.push(newItem(charCode));
      }
      this.items.splice(0, this.items.length, ...items);
    },
    onPreDraw: function() {
      return measureHeight();
    },
    onDraw: function(ctx) {
      var w = ctx.canvas.width / ctx.getTransform().a;
      var h = measureHeight();
      if (this.highlight) {
        ctx.fillStyle = Theme.colorBackgroundSelection;
        ctx.fillRect(0, 0, w, h - 2);
      }
      ctx.font = '12px Menlo';
      var x = 0;
      var y = 12;
      x += 28;
      ctx.fillStyle = !this.running ? (!this.highlight ? Theme.colorTextDarker : Theme.colorTextDark) : Theme.colorText2;
      var address = '0x' + this.address.toString(16).zfill(2 * asmdb.getInstance().UNIT);
      ctx.fillText(address, x, y);
      x += measureLength(address.length);
      x += measureLength(2);
      ctx.fillStyle = Theme.colorText;
      ctx.fillText(this.value.toString(16).zfill(2), x, y);
      x += measureLength(2);
      if (this.value >= 0x21 && this.value <= 0x7e) {
        x += measureLength(1);
        ctx.fillStyle = Theme.colorTextDark;
        var charCode = String.fromCharCode(this.value);
        ctx.fillText(charCode, x, y);
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.byte-container {
  height: 18px;
  > span {
    line-height: 16px;
    font-size: 12px;
    color: transparent;
    white-space: nowrap;
  }
  > span:first-of-type {
    margin-left: 28px;
  }
}
</style>
