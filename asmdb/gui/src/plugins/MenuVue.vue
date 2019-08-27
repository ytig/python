<template>
  <div ref="menuContainer" v-show="show" class="menu-container" :style="{left:left+'px',top:top+'px'}">
    <div v-for="(item, index) in items" :key="index">
      <span>{{item[0]}}</span>
      <span>{{item[1]}}</span>
    </div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      left: 0,
      top: 0,
      show: false,
      items: [],
      listener: null
    };
  },
  methods: {
    alert: function(event, items, listener) {
      this.left = event.clientX;
      this.top = event.clientY;
      this.show = true;
      this.items = items;
      this.listener = listener;
    },
    close: function() {
      this.show = false;
      this.items = [];
      this.listener = null;
    },
    onMouseDown: function(event) {
      var intercept = this.show;
      var inner = false;
      var node = event.target;
      while (node) {
        if (node == this.$refs.menuContainer) {
          inner = true;
          break;
        }
        node = node.parentNode;
      }
      if (!inner) {
        this.close();
      }
      return intercept;
    },
    onClick: function(event) {
      if (this.show) {
        var index = -1;
        var node = event.target;
        while (node) {
          if (node.parentNode == this.$refs.menuContainer) {
            index = new Array(...this.$refs.menuContainer.childNodes).indexOf(node);
            break;
          }
          node = node.parentNode;
        }
        if (index >= 0) {
          this.onClickItem(index);
        }
      }
    },
    onKeyDown: function(event) {
      return this.show;
    },
    onClickItem: function(index) {
      this.listener(index);
      this.close();
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.menu-container {
  position: fixed;
  display: inline-block;
  background: @color-dark-background;
  box-shadow: 0px 0px 6px @color-border-shadow;
  padding-top: 4px;
  padding-bottom: 4px;
  min-width: 147px;
  > div {
    padding-left: 12px;
    padding-right: 6px;
    line-height: 22px;
    display: flex;
    justify-content: space-between;
    > span:first-child {
      font-family: 'PingFang SC';
      font-size: 12px;
      color: @color-menu-text;
    }
    > span:last-child {
      font-family: 'PingFang SC';
      font-size: 12px;
      color: @color-menu-dark-text;
    }
  }
  > div:hover {
    background: @color-hover-background;
  }
}
</style>
