<template>
  <div class="instruction-container">
    <div @mouseover="onMouseOverBpt" @mouseout="onMouseOutBpt" @click="onClickBpt"></div>
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
      hoverBpt: false,
      items: []
    };
  },
  props: {
    address: Number,
    mnemonic: String,
    op_str: String,
    comment: String,
    highlight: Boolean,
    running: Boolean,
    breaking: Number,
    group: Number
  },
  created: function() {
    this.needLayout.push('address', 'mnemonic', 'op_str', 'comment', 'group');
    this.needDraw.push('highlight', 'running', 'breaking');
  },
  methods: {
    onLayout: function() {
      var items = [];
      var address = '0x' + this.address.toString(16).zfill(2 * asmdb.getInstance().UNIT);
      items.push(newItem(address));
      items.push(newItem('&nbsp;&nbsp;'));
      items.push(newItem(this.mnemonic));
      var space = '';
      for (var i = 0; i < this.group - this.mnemonic.length; i++) {
        space += '&nbsp;';
      }
      space += '&nbsp;';
      items.push(newItem(space));
      items.push(newItem(this.op_str));
      if (this.comment) {
        items.push(newItem('&nbsp;&nbsp;'));
        for (var s of this.comment) {
          items.push(newItem(s == ' ' ? '&nbsp;' : s));
        }
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
      x += 12;
      var color = null;
      switch (this.breaking) {
        case 0:
          if (this.hoverBpt) {
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
      ctx.fillStyle = !this.running ? (!this.highlight ? Theme.colorTextDarker : Theme.colorTextDark) : Theme.colorText2;
      var address = '0x' + this.address.toString(16).zfill(2 * asmdb.getInstance().UNIT);
      ctx.fillText(address, x, y);
      x += measureLength(address.length);
      x += measureLength(2);
      ctx.fillStyle = Theme.colorText2;
      ctx.fillText(this.mnemonic, x, y);
      x += Math.max(measureLength(this.mnemonic.length), measureLength(this.group));
      x += measureLength(1);
      ctx.fillStyle = Theme.colorText;
      ctx.fillText(this.op_str, x, y);
      x += measureLength(this.op_str.length);
      if (this.comment) {
        x += measureLength(2);
        ctx.fillStyle = Theme.colorTextDark;
        ctx.fillText(this.comment, x, y);
      }
    },
    onMouseOverBpt: function() {
      this.hoverBpt = true;
      this.draw();
    },
    onMouseOutBpt: function() {
      this.hoverBpt = false;
      this.draw();
    },
    onClickBpt: function() {
      if (!this.breaking) {
        asmdb.getInstance().bpt([], [{ address: this.address, disable: false, comment: '' }]);
      } else {
        asmdb.getInstance().bpt([{ address: this.address }], []);
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.instruction-container {
  height: 18px;
  > div {
    position: absolute;
    width: 28px;
    height: 18px;
    cursor: pointer;
  }
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
