<template>
  <div ref="container" class="recycler-container" @scroll="onScroll">
    <div v-for="item in items" :key="item.idx" :idx="item.idx">
      <slot :item="item"></slot>
    </div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      hst: null
    };
  },
  props: {
    items: Array
  },
  beforeUpdate: function() {
    this.hstSet();
  },
  updated: function() {
    this.hstGet();
  },
  methods: {
    hstSet: function() {
      var container = this.$refs.container;
      var scrollTop = container.scrollTop;
      for (var i = 0; i < container.children.length; i++) {
        var child = container.children[i];
        scrollTop -= child.scrollHeight;
        if (scrollTop < 0) {
          this.hst = [child.getAttribute('idx'), child.scrollHeight + scrollTop];
          return;
        }
      }
      this.hst = null;
    },
    hstGet: function() {
      var container = this.$refs.container;
      var scrollTop = 0;
      if (this.hst) {
        for (var i = 0; i < container.children.length; i++) {
          var child = container.children[i];
          if (child.getAttribute('idx') == this.hst[0]) {
            scrollTop += this.hst[1];
            container.scrollTop = scrollTop;
            return;
          }
          scrollTop += child.scrollHeight;
        }
      }
      container.scrollTop = (container.scrollHeight - container.clientHeight) / 2;
    },
    onScroll: function() {
      var container = this.$refs.container;
      if (container.scrollTop <= container.scrollHeight / 5) {
        console.log('scroll to top');
      } else if (container.scrollHeight - container.clientHeight - container.scrollTop <= container.scrollHeight / 5) {
        console.log('scroll to bottom');
      } else {
        console.log('scroll in middle');
      }
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
