<template>
  <div ref="container" class="terminal-parent-container" @wheel="onWheel">
    <canvas ref="canvas1" class="terminal-parent-draw"></canvas>
    <canvas ref="canvas2" class="terminal-parent-draw"></canvas>
    <div class="terminal-parent-item" v-for="item in viewport" :key="item.id" :style="item.style_">
      <slot v-if="item.key!=null" :item="item.val" :index="item.key" :offset="item.top" :context="context" :scrolling="scrolling"></slot>
    </div>
  </div>
</template>

<script>
import resize from '@/scripts/resize';

function comparePosition(p1, p2) {
  var i = p1.index - p2.index;
  if (i != 0) {
    return i > 0 ? 1 : -1;
  }
  var o = p1.offset - p2.offset;
  if (o != 0) {
    return o > 0 ? 1 : -1;
  }
  return 0;
}

export default {
  data: function() {
    return {
      position: { index: 0, offset: 0 },
      remnant: null,
      attach: true,
      column: 0,
      viewport: [],
      unique: 0,
      counter: 0,
      context: '',
      scrolling: false
    };
  },
  props: {
    lineHeight: Number,
    source: Object
  },
  watch: {
    source: function(newValue, oldValue) {
      this.attach = true;
      this.scrollBy(0);
    },
    'source.invalidate': function(newValue, oldValue) {
      this.scrollBy(0);
    }
  },
  mounted: function() {
    var w = this.$refs.container.clientWidth;
    var h = screen.height;
    this.$refs.canvas1.style.width = this.$refs.canvas2.style.width = w + 'px';
    this.$refs.canvas1.style.height = this.$refs.canvas2.style.height = h + 'px';
    resize.registerEvent(this);
    this.onResize();
  },
  destroyed: function() {
    resize.unregisterEvent(this);
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
    getMaxPosition: function() {
      var index = 0;
      var offset = 0;
      if (this.source.length > 0) {
        index = this.source.length - 1;
        offset = this.source[index].lineCount - 1;
      }
      var column = this.column;
      while (--column > 0) {
        offset--;
        if (offset < 0) {
          index--;
          if (index < 0) {
            index = offset = 0;
            break;
          }
          offset = this.source[index].lineCount - 1;
        }
      }
      return {
        index: index,
        offset: offset
      };
    },
    attachTo: function() {
      this.remnant = null;
      if (!this.attach) {
        this.attach = true;
        this.scrollBy(0);
      }
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
      if (this.source.length > 0) {
        var max = this.getMaxPosition();
        if (this.attach && delta >= 0) {
          this.position.index = max.index;
          this.position.offset = max.offset;
        } else {
          this.position.offset += delta;
          while (this.position.offset < 0) {
            if (this.position.index == 0) {
              this.position.offset = 0;
              break;
            }
            this.position.offset += this.source[--this.position.index].lineCount;
          }
          while (this.position.offset >= this.source[this.position.index].lineCount) {
            if (this.position.index == this.source.length - 1) {
              this.position.offset = this.source[this.position.index].lineCount - 1;
              break;
            }
            this.position.offset -= this.source[this.position.index++].lineCount;
          }
        }
        if (comparePosition(this.position, max) > 0) {
          this.position.index = max.index;
          this.position.offset = max.offset;
        }
        this.attach = this.position.index == max.index && this.position.offset == max.offset;
      } else {
        this.position.index = 0;
        this.position.offset = 0;
        this.attach = true;
      }
      this.$emit('scroll2', this.getPosition());
      this.invalidate();
    },
    onWheel: function(event) {
      if (event.cancelable) {
        this.remnant = 0;
      }
      if (this.remnant != null) {
        this.remnant += event.deltaY;
        var delta = parseInt(Math.abs(this.remnant) / this.lineHeight) * (this.remnant > 0 ? 1 : -1);
        if (delta != 0) {
          this.remnant -= delta * this.lineHeight;
          this.scrollBy(delta);
        }
      }
    },
    onResize: function() {
      var column = this.$refs.container.clientHeight / this.lineHeight;
      if (this.column != column) {
        this.column = column;
        this.scrollBy(0);
      }
    },
    invalidate: function() {
      var scrollTop = 0;
      for (var i = 0; i < this.position.index; i++) {
        scrollTop += this.source[i].lineCount * this.lineHeight;
      }
      scrollTop += this.position.offset * this.lineHeight;
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
      var sumTop = scrollTop - this.position.offset * this.lineHeight;
      var i = this.position.index - 1;
      while (++i in this.source) {
        var item = {
          key: i,
          val: this.source[i],
          top: sumTop,
          style_: {
            height: this.source[i].lineCount * this.lineHeight + 'px',
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
        sumTop += this.source[i].lineCount * this.lineHeight;
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

.terminal-parent-container {
  overflow: hidden;
  position: relative;
  contain: strict;
  .terminal-parent-draw {
    position: absolute;
    contain: strict;
    pointer-events: none;
  }
  .terminal-parent-item {
    position: absolute;
    contain: strict;
    width: 100%;
  }
}
</style>
