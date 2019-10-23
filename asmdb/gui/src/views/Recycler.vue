<template>
  <div ref="container" class="recycler-container" :style="show_" @scroll="onScroll">
    <div class="recycler-fill" :style="style_"></div>
    <div class="recycler-item" v-for="(item, index) in viewport" :key="index" :style="item.style_">
      <slot v-if="item.key>=0" :item="item.val" :index="item.key" :scrolling="scrolling"></slot>
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
      scrolling: false,
      style_: { transform: 'translateY(0px)' }
    };
  },
  props: {
    show: Boolean,
    lineHeight: Number,
    source: Object
  },
  computed: {
    show_: function() {
      if (this.show) {
        return {};
      } else {
        return {
          opacity: 0,
          overflowY: 'hidden',
          pointerEvents: 'none'
        };
      }
    }
  },
  watch: {
    show: function(newValue, oldValue) {
      if (newValue) {
        this.$emit('scroll2', this.getPosition());
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
    var length = 3 * Math.ceil(screen.height / this.lineHeight);
    var viewport = [];
    for (var i = 0; i < length; i++) {
      viewport[i] = { key: -1, val: null, style_: { height: this.lineHeight + 'px', transform: 'translateY(0px)' } };
    }
    this.viewport.splice(0, this.viewport.length, ...viewport);
    if (this.show) {
      this.$emit('scroll2', this.getPosition());
    }
    this.invalidate();
  },
  methods: {
    getPageSize: function() {
      return parseInt(maxHeight / this.lineHeight / 3);
    },
    getPosition: function() {
      var scrollTop = this.$refs.container.scrollTop;
      var position = {};
      position.index = this.page * this.getPageSize() + parseInt(scrollTop / this.lineHeight);
      position.offset = scrollTop % this.lineHeight;
      return position;
    },
    scrollTo: function(position) {
      var pageSize = this.getPageSize();
      var pageLength = 1 + Math.max(Math.ceil(this.source.length / pageSize) - 3, 0);
      var container = this.$refs.container;
      var maxScrollTop = Math.max(this.lineHeight * this.source.length - container.clientHeight, 0);
      var scrollTop = position.index * this.lineHeight + position.offset;
      scrollTop = Math.min(Math.max(scrollTop, 0), maxScrollTop);
      var page = parseInt(scrollTop / (this.lineHeight * pageSize) - 0.741);
      page = Math.min(Math.max(page, 0), pageLength - 1);
      this.page = page;
      container.scrollTop = scrollTop - this.lineHeight * this.page * pageSize;
      this.position.index = parseInt(scrollTop / this.lineHeight);
      this.position.offset = scrollTop % this.lineHeight;
      this.invalidate();
    },
    onScroll: function() {
      this.counter++;
      this.scrolling = true;
      var counter = this.counter;
      setTimeout(() => {
        if (counter != this.counter) {
          return;
        }
        this.scrolling = false;
        this.onScrollStop();
      }, 147);
      this.$emit('scroll2', this.getPosition());
      if (this.changePage()) {
        return;
      }
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
        var translateY;
        if (key >= 0) {
          translateY = this.lineHeight * (key - this.page * pageSize);
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
  overflow-x: hidden;
  overflow-y: scroll;
  contain: strict;
  .recycler-fill {
    position: fixed;
    width: 1px;
    height: 1px;
  }
  .recycler-item {
    position: fixed;
    contain: strict;
    width: 100%;
  }
}
</style>
