<template>
  <div class="instruction-container"></div>
</template>

<script>
import Theme from '@/styles/theme';
import asmdb from '@/scripts/asmdb';

function measureTextWidth(length) {
  return length * 7.224609375;
}

function measureTextHeight() {
  return 14;
}

function measureViewWidth() {
  //todo
  return 0;
}

function measureViewHeight() {
  return measureTextHeight() + 4;
}

export default {
  measureWidth: measureViewWidth,
  measureHeight: measureViewHeight,
  data: function() {
    return {
      dirty: false,
      items: []
    };
  },
  props: {
    canvasContext: String,
    lazyLayout: Boolean
  },
  computed: {
    self: function() {
      return {
        canvasContext: this.canvasContext,
        lazyLayout: this.lazyLayout
      };
    }
  },
  watch: {
    self: function(newValue, oldValue) {
      var needLayout = false;
      var needDraw = false;
      if (false) {
        needLayout = true;
        needDraw = true;
      }
      if (newValue.canvasContext != oldValue.canvasContext) {
        needDraw = true;
      }
      if (!newValue.lazyLayout) {
        if (needLayout || this.dirty) {
          this.layout();
          this.dirty = false;
        }
      } else {
        if (needLayout) {
          this.dirty = true;
        }
      }
      if (needDraw) {
        this.draw();
      }
    }
  },
  mounted: function() {
    if (!this.lazyLayout) {
      this.layout();
    } else {
      this.dirty = true;
    }
    this.draw();
  },
  methods: {
    layout: function() {
      //todo
    },
    draw: function() {
      var self = this.self;
      var cc = self.canvasContext.split(';');
      var h = measureViewHeight();
      var t = parseInt(cc[0]);
      for (var i of cc[1].split(',')) {
        var c = getContext(parseInt(i), t, h);
        if (c != null) {
          this.draw_(c);
        }
      }
    },
    draw_: function(ctx) {
      //todo
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
