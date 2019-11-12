<template>
  <div ref="container" class="scroller-container" @wheel="onWheel">
    <div class="scroller-item" v-for="(item, index) in viewport" :key="index" :style="item.style_">
      <slot v-if="item.key!=null" :item="item.val" :index="item.key" :offset="item.top" :context="context" :scrolling="scrolling"></slot>
    </div>
    <canvas ref="canvas1" class="scroller-draw"></canvas>
    <canvas ref="canvas2" class="scroller-draw"></canvas>
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
    source: Object
  },
  watch: {
    source: function(newValue, oldValue) {
      this.position.index = this.position.offset = 0;
      this.scrollBy(0);
    },
    'source.invalidate': function(newValue, oldValue) {
      if (this.position.offset >= this.source[this.position.index].height) {
        this.scrollBy(0);
      } else {
        this.invalidate();
      }
    }
  },
  mounted: function() {
    var minLineHeight = 12;
    var length = Math.ceil(screen.height / minLineHeight) + 1;
    var viewport = [];
    for (var i = 0; i < length; i++) {
      viewport[i] = { key: null, val: null, top: 0, style_: { height: '0px', transform: 'translateY(0px)' } };
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
    getPosition: function() {
      return {
        index: this.position.index,
        offset: this.position.offset
      };
    },
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
      var index = this.position.index;
      var offset = this.position.offset;
      if (index in this.source) {
        offset += delta;
        while (offset < 0) {
          if (index - 1 in this.source) {
            offset += this.source[index].height;
            index--;
          } else {
            offset = 0;
            break;
          }
        }
        while (offset >= this.source[index].height) {
          if (index + 1 in this.source) {
            offset -= this.source[index].height;
            index++;
          } else {
            offset = this.source[index].height;
            break;
          }
        }
        if (!(index + 1 in this.source)) {
          offset = 0;
        }
      }
      this.position.index = index;
      this.position.offset = offset;
      this.$emit('scroll2', this.getPosition());
      this.invalidate();
    },
    onWheel: function(event) {
      this.scrollBy(event.deltaY);
    },
    invalidate: function() {
      var scrollTop = this.position.offset;
      if (this.position.index < 0) {
        for (var i = this.position.index; i < 0; i++) {
          scrollTop -= this.source[i].height;
        }
      } else {
        for (var i = 0; i < this.position.index; i++) {
          scrollTop += this.source[i].height;
        }
      }
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
      var sum = scrollTop - this.position.offset;
      for (var i = 0; i < this.viewport.length; i++) {
        //todo dynmic viewport
        var o = (((this.position.index + i) % this.viewport.length) + this.viewport.length) % this.viewport.length;
        var slot = this.viewport[o];
        var key = this.position.index + i;
        var val = null;
        var top = sum;
        var add = 0;
        if (key in this.source) {
          val = this.source[key];
          add = val.height;
        } else {
          key = null;
        }
        sum += add;
        if (slot.key != key) {
          slot.key = key;
        }
        if (slot.val != val) {
          slot.val = val;
        }
        if (slot.top != top) {
          slot.top = top;
        }
        if (!this.scrolling) {
          var height = add + 'px';
          var transform = 'translateY(' + (top - scrollTop) + 'px)';
          if (slot.style_.height != height) {
            slot.style_.height = height;
          }
          if (slot.style_.transform != transform) {
            slot.style_.transform = transform;
          }
        }
      }
      var cvsHeight = screen.height;
      var sumHeight = -this.position.offset;
      var i = this.position.index;
      while (i in this.source) {
        sumHeight += this.source[i].height;
        if (sumHeight >= cvsHeight) {
          return;
        }
        i++;
      }
      var cvsWidth = this.$refs.container.clientWidth;
      for (var token of tokens) {
        var ctx = getContext(token, scrollTop + sumHeight, cvsHeight);
        if (ctx != null) {
          ctx.clearRect(0, 0, cvsWidth, cvsHeight);
        }
      }
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
