<template>
  <div ref="container" class="recycler-container" @scroll="onScroll">
    <div v-for="item in items" :key="item.idx % items.length" :idx="item.idx">
      <slot :item="item"></slot>
    </div>
  </div>
</template>

<script>
class Scrolling {
  constructor() {
    this.tag = 0;
    this.scrolling = 0;
    this.runnables = [];
  }

  onScroll(edge) {
    if (!edge) {
      var tag = this.tag;
      this.scrolling++;
      setTimeout(() => {
        if (tag != this.tag) {
          return;
        }
        this.scrolling--;
        if (this.scrolling == 0) {
          this.runnables.reverse();
          while (this.runnables.length > 0) {
            this.runnables.pop()();
          }
        }
      }, 147);
    } else {
      this.tag++;
      this.scrolling = 0;
      this.runnables.reverse();
      while (this.runnables.length > 0) {
        this.runnables.pop()();
      }
    }
  }

  postStop(runnable) {
    if (!this.scrolling) {
      runnable();
    } else {
      this.runnables.push(runnable);
    }
  }
}

export default {
  data: function() {
    return {
      scrolling: new Scrolling()
    };
  },
  props: {
    items: Array
  },
  updated: function() {
    var posn = this.items.posn;
    var container = this.$refs.container;
    var scrollTop = 0;
    if (posn) {
      for (var i = 0; i < container.children.length; i++) {
        var child = container.children[i];
        if (child.getAttribute('idx') == posn[0]) {
          scrollTop += posn[1];
          container.scrollTop = scrollTop;
          return;
        }
        scrollTop += child.scrollHeight;
      }
    }
  },
  methods: {
    getPosition: function() {
      var container = this.$refs.container;
      var scrollTop = container.scrollTop;
      for (var i = 0; i < container.children.length; i++) {
        var child = container.children[i];
        scrollTop -= child.scrollHeight;
        if (scrollTop < 0) {
          return [child.getAttribute('idx'), child.scrollHeight + scrollTop];
        }
      }
      return null;
    },
    onScroll: function() {
      var container = this.$refs.container;
      var isTop = container.scrollTop <= 0;
      var isBottom = container.scrollTop >= container.scrollHeight - container.clientHeight;
      this.scrolling.onScroll(isTop || isBottom);
      var loadmore = 0;
      if (container.scrollTop < container.scrollHeight / 6) {
        loadmore = -1;
      } else if (container.scrollHeight - container.clientHeight - container.scrollTop < container.scrollHeight / 6) {
        loadmore = 1;
      }
      this.$emit('loadmore', loadmore);
    },
    postStop: function(runnable) {
      this.scrolling.postStop(runnable);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.recycler-container {
  overflow: scroll;
}
</style>
