<template>
  <div ref="container" class="recycler-container" @scroll="onScroll">
    <div v-for="item in items" :key="item.idx % items.length" :idx="item.idx">
      <slot :item="item"></slot>
    </div>
  </div>
</template>

<script>
function preventOverScroll(el) {
  var prevent = 0;
  el.addEventListener('wheel', event => {
    if (event.cancelable) {
      prevent = 0;
    } else {
      if (prevent * event.deltaY <= 0) {
        prevent = 0;
      } else {
        el.style.overflowY = 'hidden';
        requestAnimationFrame(() => {
          el.style.overflowY = 'scroll';
        });
      }
    }
  });
  el.addEventListener('scroll', event => {
    if (el.scrollTop <= 0) {
      prevent = -1;
    }
    if (el.scrollTop >= el.scrollHeight - el.clientHeight) {
      prevent = 1;
    }
  });
}

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
      scrolling: new Scrolling(),
      hst: [],
      posn: null
    };
  },
  props: {
    items: Array
  },
  mounted: function() {
    preventOverScroll(this.$refs.container);
  },
  beforeUpdate: function() {
    if (!this.posn) {
      this.hstSet() && this.hstGet();
    }
  },
  updated: function() {
    var posn = this.posn;
    this.posn = null;
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
    container.scrollTop = (container.scrollHeight - container.clientHeight) / 2;
  },
  methods: {
    hstSet: function() {
      var container = this.$refs.container;
      var scrollTop = container.scrollTop;
      for (var i = 0; i < container.children.length; i++) {
        var child = container.children[i];
        scrollTop -= child.scrollHeight;
        if (scrollTop < 0) {
          var posn = [child.getAttribute('idx'), child.scrollHeight + scrollTop];
          this.hst.splice(this.hst.length, 0, posn);
          return true;
        }
      }
      return false;
    },
    hstGet: function() {
      if (this.hst.length <= 0) {
        return false;
      } else {
        var posn = this.hst.splice(this.hst.length - 1, 1)[0];
        this.posn = posn;
        return true;
      }
    },
    onScroll: function() {
      var container = this.$refs.container;
      var isTop = container.scrollTop <= 0;
      var isBottom = container.scrollTop >= container.scrollHeight - container.clientHeight;
      this.scrolling.onScroll(isTop || isBottom);
      var loadmore = 0;
      if (container.scrollTop <= container.scrollHeight / 5) {
        loadmore = -1;
      } else if (container.scrollHeight - container.clientHeight - container.scrollTop <= container.scrollHeight / 5) {
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
