<template>
  <div ref="container" class="recycler-container" @wheel.passive="onWheel">
    <div class="recycler-item" v-for="(item, index) in viewport" :key="index" :style="item.style_">
      <slot v-if="show&&item.key>=0" :item="item.val" :index="item.key" :context="context" :scrolling="scrolling"></slot>
    </div>
    <canvas ref="canvas1" class="recycler-draw"></canvas>
    <canvas ref="canvas2" class="recycler-draw"></canvas>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      position: { index: 0, offset: 0 },
      viewport: [],
      counter: 0,
      context: '',
      scrolling: false
    };
  },
  props: {
    show: Boolean,
    lineHeight: Number,
    source: Object
  },
  watch: {
    show: function(newValue, oldValue) {
      if (!newValue) {
        for (var view of [this.$refs.canvas1, this.$refs.canvas2]) {
          var context = view.getContext('2d');
          context.resetTransform();
          context.clearRect(0, 0, view.width, view.height);
        }
      }
    },
    source: function(newValue, oldValue) {
      this.invalidate();
    },
    'source.invalidate': function(newValue, oldValue) {
      this.invalidate();
    }
  },
  mounted: function() {
    var length = Math.ceil(screen.height / this.lineHeight) + 1;
    var viewport = [];
    for (var i = 0; i < length; i++) {
      viewport[i] = { key: -1, val: null, ctx: null, style_: { height: this.lineHeight + 'px', transform: 'translateY(0px)' } };
    }
    this.viewport.splice(0, this.viewport.length, ...viewport);
    var w = this.$refs.container.clientWidth;
    var h = length * this.lineHeight;
    for (var view of [this.$refs.canvas1, this.$refs.canvas2]) {
      view.style.width = w + 'px';
      view.style.height = h + 'px';
    }
    this.scrollTo(this.position);
  },
  destroyed: function() {
    delContext(this.$refs.canvas1);
    delContext(this.$refs.canvas2);
  },
  methods: {
    getPosition: function() {
      return {
        index: this.position.index,
        offset: this.position.offset
      };
    },
    scrollTo: function(position) {
      this.scrolling = true;
      var counter = ++this.counter;
      setTimeout(() => {
        if (counter != this.counter) {
          return;
        }
        this.scrolling = false;
        this.invalidate();
      }, 147);
      var scrollTop = position.index * this.lineHeight + position.offset;
      var maxScrollTop = this.source.length * this.lineHeight - this.$refs.container.clientHeight;
      scrollTop = Math.min(Math.max(scrollTop, 0), maxScrollTop);
      this.position.index = parseInt(scrollTop / this.lineHeight);
      this.position.offset = scrollTop % this.lineHeight;
      this.$emit('scroll2', this.getPosition());
      this.invalidate();
    },
    onWheel: function(event) {
      if (!this.show) {
        return;
      }
      this.scrollTo({
        index: this.position.index,
        offset: this.position.offset + event.deltaY
      });
    },
    invalidate: function() {
      var scrollTop = this.position.index * this.lineHeight + this.position.offset;
      var height = this.viewport.length * this.lineHeight;
      var index = parseInt(scrollTop / height);
      var offset = scrollTop % height;
      var views = [this.$refs.canvas1, this.$refs.canvas2];
      var tokens = [];
      for (var i = 0; i < views.length; i++) {
        var o = (index + i) % views.length;
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
      for (var i = 0; i < this.viewport.length; i++) {
        var o = (this.position.index + i) % this.viewport.length;
        var slot = this.viewport[o];
        var key = this.position.index + i;
        if (key < 0 || key >= this.source.length) {
          key = -1;
        }
        var val = null;
        if (key in this.source) {
          val = this.source[key];
        }
        var translateY;
        if (key >= 0) {
          translateY = this.lineHeight * (key - this.position.index) - this.position.offset;
        } else {
          translateY = -this.lineHeight;
        }
        var transform = 'translateY(' + translateY + 'px)';
        if (slot.key != key) {
          slot.key = key;
        }
        if (slot.val != val) {
          slot.val = val;
        }
        if (!this.scrolling) {
          if (slot.style_.transform != transform) {
            slot.style_.transform = transform;
          }
        }
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.recycler-container {
  overflow: hidden;
  contain: strict;
  .recycler-item {
    position: fixed;
    contain: strict;
    width: 100%;
  }
  .recycler-draw {
    position: fixed;
    contain: strict;
    pointer-events: none;
  }
}
</style>
