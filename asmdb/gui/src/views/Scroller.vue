<template>
  <div ref="container" class="scroller-container" @wheel="onWheel">
    <div class="scroller-item" v-for="(item, index) in viewport" :key="index" :style="item.style_">
      <slot v-if="item.key!=null" :item="item.val" :index="item.key" :context="context" :scrolling="scrolling"></slot>
    </div>
    <canvas ref="canvas1" class="scroller-draw"></canvas>
    <canvas ref="canvas2" class="scroller-draw"></canvas>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      scrollTop: 0,
      viewport: [],
      counter: 0,
      context: '',
      scrolling: false
    };
  },
  props: {
    source: Object
  },
  watch: {
    source: function(newValue, oldValue) {
      this.invalidate();
    },
    'source.invalidate': function(newValue, oldValue) {
      this.invalidate();
    }
  },
  mounted: function() {
    var minHeight = 12;
    var length = Math.ceil(screen.height / minHeight) + 1;
    var viewport = [];
    for (var i = 0; i < length; i++) {
      viewport[i] = { key: null, val: null, style_: { transform: 'translateY(0px)' } };
    }
    this.viewport.splice(0, this.viewport.length, ...viewport);
    var w = this.$refs.container.clientWidth;
    var h = screen.height;
    this.$refs.canvas1.style.width = w + 'px';
    this.$refs.canvas1.style.height = h + 'px';
    this.$refs.canvas2.style.width = w + 'px';
    this.$refs.canvas2.style.height = h + 'px';
    this.scrollBy(0);
  },
  destroyed: function() {
    delContext(this.$refs.canvas1);
    delContext(this.$refs.canvas2);
  },
  methods: {
    scrollBy: function(delta) {
      emptySelection();
      this.scrolling = true;
      var counter = ++this.counter;
      setTimeout(() => {
        if (counter != this.counter) {
          return;
        }
        this.scrolling = false;
        this.invalidate();
      }, 147);
      this.scrollTop += delta; //todo
      this.invalidate();
    },
    onWheel: function(event) {
      this.scrollBy(event.deltaY);
    },
    invalidate: function() {
      var scrollTop = this.scrollTop;
      var height = screen.height;
      var index = parseSignedInt(scrollTop / height);
      var offset = scrollTop - index * height;
      var views = [this.$refs.canvas1, this.$refs.canvas2];
      var tokens = [];
      for (var i = 0; i < views.length; i++) {
        var o = (((index + i) % views.length) + views.length) % views.length;
        var view = views[o];
        var transform = 'translateY(' + (height * i - offset) + 'px)';
        if (view.style.transform != transform) {
          view.style.transform = transform;
        }
        if (view.index != index + i) {
          view.index = index + i;
          view.token = setContext(view, view.index * height, height);
        }
        tokens.push(view.token);
      }
      this.context = tokens.sort().join();
      //todo
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.scroller-container {
  overflow: hidden;
  contain: strict;
  .scroller-item {
    position: fixed;
    contain: strict;
    width: 100%;
  }
  .scroller-draw {
    position: fixed;
    contain: strict;
    pointer-events: none;
  }
}
</style>
