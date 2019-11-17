<template>
  <div class="instruction-container"></div>
</template>

<script>
import Theme from '@/styles/theme';
import asmdb from '@/scripts/asmdb';
import InfiniteMixin from './InfiniteMixin';

function measureWidth() {
  //todo
  return 0;
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
  props: {},
  methods: {
    onLayout: function() {
      //todo
    },
    onPreDraw: function() {
      return measureHeight();
    },
    onDraw: function(ctx) {
      //todo
      ctx.font = '12px Menlo';
      var x = 0;
      var y = 12;
      x += 12 + 16;
      ctx.fillStyle = Theme.colorTextDarker;
      ctx.fillText('0x12345678  ', x, y);
      x += measureText(12);
      ctx.fillStyle = Theme.colorText2;
      ctx.fillText('ldr    ', x, y);
      x += measureText(7);
      ctx.fillStyle = Theme.colorText;
      ctx.fillText('r0, r1', x, y);
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
