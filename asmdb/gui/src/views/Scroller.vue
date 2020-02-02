<template>
  <div ref="container" class="scroller-container" @wheel="onWheel">
    <canvas ref="canvas1" class="scroller-draw"></canvas>
    <canvas ref="canvas2" class="scroller-draw"></canvas>
    <div class="scroller-item" v-for="item in viewport" :key="item.id" :style="item.style_">
      <slot v-if="item.key!=null" :item="item.val" :index="item.key" :offset="item.top" :context="context" :scrolling="scrolling"></slot>
    </div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      position: { index: 0, offset: 0 },
      viewport: [],
      unique: 0,
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
    var w = this.$refs.container.clientWidth;
    var h = screen.height;
    this.$refs.canvas1.style.width = this.$refs.canvas2.style.width = w + 'px';
    this.$refs.canvas1.style.height = this.$refs.canvas2.style.height = h + 'px';
    this.scrollBy(0);
  },
  beforeDestroy: function() {
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
        if (counter != this.counter || this._isDestroyed) {
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
            offset += this.source[index - 1].height;
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
      var canvasHeight = screen.height;
      var index = parseSignedInt(scrollTop / canvasHeight);
      var offset = scrollTop - index * canvasHeight;
      var views = [this.$refs.canvas1, this.$refs.canvas2];
      var tokens = [];
      for (var i = 0; i < views.length; i++) {
        var o = (((index + i) % views.length) + views.length) % views.length;
        var view = views[o];
        var transform = 'translateY(' + (canvasHeight * i - offset) + 'px)';
        if (view.style.transform != transform) {
          view.style.transform = transform;
        }
        if (view.index != index + i) {
          view.index = index + i;
          view.token = setContext(view, view.index * canvasHeight, canvasHeight);
        }
        tokens.push(view.token);
      }
      this.context = tokens.sort().join();
      var items = [];
      var viewport = new Array(...this.viewport);
      var sumTop = scrollTop - this.position.offset;
      var i = this.position.index - 1;
      while (++i in this.source) {
        var item = {
          key: i,
          val: this.source[i],
          top: sumTop,
          style_: {
            height: this.source[i].height + 'px',
            transform: 'translateY(' + (sumTop - scrollTop) + 'px)'
          }
        };
        for (var j = viewport.length - 1; j >= 0; j--) {
          var slot = viewport[j];
          if (slot.key == item.key) {
            if (slot.val != item.val) {
              slot.val = item.val;
            }
            if (slot.top != item.top) {
              slot.top = item.top;
            }
            if (!this.scrolling) {
              if (slot.style_.height != item.style_.height) {
                slot.style_.height = item.style_.height;
              }
              if (slot.style_.transform != item.style_.transform) {
                slot.style_.transform = item.style_.transform;
              }
            }
            viewport.splice(j, 1);
            item = null;
            break;
          }
        }
        if (item) {
          items.push(item);
        }
        sumTop += this.source[i].height;
        if (sumTop - scrollTop > canvasHeight) {
          break;
        }
      }
      for (var slot of viewport) {
        var item = items.length > 0 ? items.pop() : null;
        if (item) {
          slot.key = item.key;
          slot.val = item.val;
          slot.top = item.top;
          if (!this.scrolling) {
            slot.style_.height = item.style_.height;
            slot.style_.transform = item.style_.transform;
          }
        } else {
          slot.key = null;
          slot.val = null;
          slot.top = 0;
          if (!this.scrolling) {
            slot.style_.height = '0px';
            slot.style_.transform = 'translateY(0px)';
          }
        }
      }
      for (var item of items) {
        item.id = this.unique++;
      }
      this.viewport.splice(this.viewport.length, 0, ...items);
      if (!this.scrolling) {
        this.viewport.sort(function(a, b) {
          return a.top - b.top;
        });
      }
      if (sumTop - scrollTop < canvasHeight) {
        for (var token of tokens) {
          getContext(token, sumTop, canvasHeight);
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
  position: relative;
  contain: strict;
  .scroller-draw {
    position: absolute;
    contain: strict;
    pointer-events: none;
  }
  .scroller-item {
    position: absolute;
    contain: strict;
    width: 100%;
  }
}
</style>
