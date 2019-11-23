<template>
  <div class="instruction-container" @mouseover="onMouseOver" @mouseout="onMouseOut"></div>
</template>

<script>
import Theme from '@/styles/theme';
import asmdb from '@/scripts/asmdb';
import InfiniteMixin from './InfiniteMixin';

function measureHeight() {
  return 18;
}

export default {
  measureHeight: measureHeight,
  mixins: [InfiniteMixin],
  data: function() {
    return {
      hoverBreaking: false,
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
    onMouseOver: function() {
      this.hoverBreaking = true;
      this.draw();
    },
    onMouseOut: function() {
      this.hoverBreaking = false;
      this.draw();
    },
    onLayout: function() {
      //todo
    },
    onPreDraw: function() {
      return measureHeight();
    },
    onDraw: function(ctx) {
      var w = ctx.canvas.width / ctx.getTransform().a;
      var h = measureHeight();
      ctx.font = '12px Menlo';
      var x = 0;
      var y = 12;
      x += 12;
      var color = null;
      switch (this.breaking) {
        case 0:
          if (this.hoverBreaking) {
            color = Theme.colorIconBreakpointDark;
          }
          break;
        case 1:
          color = Theme.colorIconBreakpoint;
          break;
        case 2:
          color = Theme.colorIconBreakpoint2;
          break;
      }
      if (color != null) {
        ctx.fillStyle = color;
        var r = 4;
        ctx.beginPath();
        ctx.arc(x + r, 16 / 2, 4, 0, 2 * Math.PI);
        ctx.closePath();
        ctx.fill();
      }
      x += 16;
      ctx.fillStyle = !this.highlight ? Theme.colorTextDarker : Theme.colorText2;
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
  > span {
    line-height: 16px;
    font-size: 12px;
    color: transparent;
  }
  > span:first-of-type {
    margin-left: 28px;
  }
}
</style>
