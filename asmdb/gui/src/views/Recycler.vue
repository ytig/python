<template>
  <div ref="container" class="recycler-container" @scroll="onScroll">
    <div class="recycler-fill" :style="style_"></div>
    <div class="recycler-item" v-for="(item, index) in viewport" :key="index" :style="item.style_">
      <slot v-if="item.key>=0" :item="item.val" :index="item.key"></slot>
    </div>
  </div>
</template>

<script>
var maxHeight = 16777216;

export default {
  data: function() {
    return {
      page: 0,
      position: { index: 0, offset: 0 },
      viewport: [],
      counter: 0,
      style_: { transform: 'translateY(0px)' }
    };
  },
  props: {
    lineHeight: Number,
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
    var length = 3 * Math.ceil(screen.height / this.lineHeight);
    var viewport = [];
    for (var i = 0; i < length; i++) {
      viewport[i] = { key: -1, val: null, style_: { transform: 'translateY(0px)' } };
    }
    this.viewport.splice(0, this.viewport.length, ...viewport);
    this.onScroll();
  },
  methods: {
    getPageSize: function() {
      //todo
      return 64;
    },
    getPosition: function() {
      var scrollTop = this.$refs.container.scrollTop;
      var position = {};
      position.index = this.page * this.getPageSize() + parseInt(scrollTop / this.lineHeight);
      position.offset = scrollTop % this.lineHeight;
      return position;
    },
    scrollTo: function(position) {
      //todo
    },
    onScroll: function() {
      this.counter++;
      this.$emit('scroll2', this.getPosition());
      if (this.changePage()) {
        return;
      }
      var counter = this.counter;
      setTimeout(() => {
        if (counter != this.counter) {
          return;
        }
        this.onScrollStop();
      }, 147);
      var minScrollTop = (this.position.index - this.viewport.length / 3) * this.lineHeight;
      var maxScrollTop = (this.position.index + this.viewport.length / 3) * this.lineHeight;
      var scrollTop_ = this.$refs.container.scrollTop + this.lineHeight * this.page * this.getPageSize();
      if (scrollTop_ < minScrollTop) {
        this.position.index -= Math.ceil((minScrollTop - scrollTop_) / this.lineHeight);
        this.invalidate();
      } else if (scrollTop_ > maxScrollTop) {
        this.position.index += Math.ceil((scrollTop_ - maxScrollTop) / this.lineHeight);
        this.invalidate();
      }
    },
    changePage: function() {
      var pageSize = this.getPageSize();
      var pageLength = 1 + Math.max(Math.ceil(this.source.length / pageSize) - 3, 0);
      var container = this.$refs.container;
      var t = container.scrollTop <= this.lineHeight * pageSize * 0.5;
      var b = container.scrollTop >= this.lineHeight * pageSize * 2.5;
      var d = 0;
      if (this.page > 0 && t) {
        d -= 1;
      }
      if (this.page < pageLength - 1 && b) {
        d += 1;
      }
      if (d != 0) {
        var position = this.getPosition();
        this.position.index = position.index;
        this.position.offset = position.offset;
        this.page += d;
        container.scrollTop -= this.lineHeight * pageSize * d;
        this.invalidate();
      }
      return d != 0;
    },
    onScrollStop: function() {
      var position = this.getPosition();
      this.position.index = position.index;
      this.position.offset = position.offset;
      this.invalidate();
    },
    invalidate: function() {
      var pageSize = this.getPageSize();
      var scrollHeight = this.lineHeight * Math.min(this.source.length - this.page * pageSize, 3 * pageSize);
      var transform_ = 'translateY(' + (scrollHeight - 1) + 'px)';
      if (this.style_.transform != transform_) {
        this.style_.transform = transform_;
      }
      var origin = this.position.index % this.viewport.length;
      for (var i = 0; i < this.viewport.length; i++) {
        var o = (origin + i) % this.viewport.length;
        var slot = this.viewport[o];
        var key = this.position.index + i;
        if (i >= (this.viewport.length * 2) / 3) {
          key -= this.viewport.length;
        }
        if (key < 0 || key >= this.source.length) {
          key = -1;
        }
        var val = null;
        if (key in this.source) {
          val = this.source[key];
        }
        var translateY = 0;
        if (key >= 0) {
          translateY = this.lineHeight * (key - this.page * pageSize);
        }
        var transform = 'translateY(' + translateY + 'px)';
        if (slot.key != key) {
          slot.key = key;
        }
        if (slot.val != val) {
          slot.val = val;
        }
        if (slot.style_.transform != transform) {
          slot.style_.transform = transform;
        }
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.recycler-container {
  overflow: scroll;
  position: relative;
  contain: content;
  .recycler-fill {
    position: absolute;
    width: 1px;
    height: 1px;
  }
  .recycler-item {
    position: absolute;
    contain: content;
  }
}
</style>
