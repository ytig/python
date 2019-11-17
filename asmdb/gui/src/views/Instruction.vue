<template>
  <div class="instruction-container"></div>
</template>

<script>
import Theme from '@/styles/theme';
import asmdb from '@/scripts/asmdb';
import InfiniteMixin from './InfiniteMixin';

function measureWidth() {
  //todo
  return 500;
}

function measureHeight() {
  return 18;
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
    address: String,
    mnemonic: String,
    op_str: String,
    highlight: Boolean,
    breaking: Number,
    group: Number
  },
  created: function() {
    this.needLayout.push('address', 'mnemonic', 'op_str', 'group');
    this.needDraw.push('highlight', 'breaking');
  },
  methods: {
    onLayout: function() {
      //todo
    },
    onPreDraw: function() {
      return measureHeight();
    },
    onDraw: function(ctx) {
      var w = measureWidth();
      var h = measureHeight();
      if (this.highlight) {
        ctx.fillStyle = Theme.colorBackgroundSelection;
        ctx.fillRect(0, 0, w, h - 2);
      }
      ctx.font = '12px Menlo';
      var x = 0;
      var y = 12;
      x += 12;
      //todo
      x += 16;
      ctx.fillStyle = !this.highlight ? Theme.colorTextDarker : Theme.colorTextDark;
      ctx.fillText(this.address, x, y);
      x += measureText(this.address);
      x += measureText(2);
      ctx.fillStyle = Theme.colorText2;
      ctx.fillText(this.mnemonic, x, y);
      x += Math.max(measureText(this.mnemonic.length), measureText(this.group));
      x += measureText(1);
      ctx.fillStyle = Theme.colorText;
      ctx.fillText(this.op_str, x, y);
      x += measureText(this.op_str);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.instruction-container {
  height: 18px;
}
</style>
