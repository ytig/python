<template>
  <div ref="container" class="recycler-container" @scroll="onScroll">
    <div class="recycler-fill" :style="_style"></div>
    <div class="recycler-item" v-for="(item, index) in viewport" :key="index" :style="item._style">
      <slot v-if="item.key>=0" :item="item.val" :index="item.key"></slot>
    </div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      position: { index: 0, offset: 0 },
      viewport: [],
      counter: 0,
      _style: { transform: 'translateY(0px)' }
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
      viewport[i] = { key: -1, val: null, _style: { transform: 'translateY(0px)' } };
    }
    this.viewport.splice(0, this.viewport.length, ...viewport);
    this.onScroll();
  },
  methods: {
    onScroll: function() {
      this.counter++;
      var container = this.$refs.container;
      this.$emit('scroll2', parseInt(container.scrollTop / this.lineHeight));
      if (container.scrollTop <= 0 || container.scrollTop >= container.scrollHeight - container.clientHeight) {
        this.onScrollStop();
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
      var scrollTop = container.scrollTop;
      if (scrollTop < minScrollTop) {
        this.position.index -= Math.ceil((minScrollTop - scrollTop) / this.lineHeight);
        this.invalidate();
      } else if (scrollTop > maxScrollTop) {
        this.position.index += Math.ceil((scrollTop - maxScrollTop) / this.lineHeight);
        this.invalidate();
      }
    },
    onScrollStop: function() {
      var container = this.$refs.container;
      var scrollTop = container.scrollTop;
      this.position.index = parseInt(scrollTop / this.lineHeight);
      this.position.offset = scrollTop % this.lineHeight;
      this.invalidate();
    },
    invalidate: function() {
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
        if (slot.key != key) {
          slot.key = key;
          var translateY = 0;
          if (key >= 0) {
            translateY = this.lineHeight * key;
          }
          slot._style.transform = 'translateY(' + translateY + 'px)';
        }
        if (slot.val != val) {
          slot.val = val;
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
