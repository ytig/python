<template>
  <div ref="menuContainer" v-show="show" class="menu-container" :style="{left:left+'px',top:top+'px',opacity:hide?0:1}">
    <div v-for="(item, index) in items" :key="index" :css-enable="item[2]">
      <span class="user-select-none">{{item[0]}}</span>
      <span class="user-select-none">{{item[1]}}</span>
    </div>
  </div>
</template>

<script>
function getChildIndex(parent, child) {
  while (child) {
    if (child.parentNode == parent) {
      return new Array(...parent.childNodes).indexOf(child);
    }
    child = child.parentNode;
  }
  return -1;
}

export default {
  data: function() {
    return {
      left: 0,
      top: 0,
      hide: false,
      show: false,
      items: [],
      listener: null
    };
  },
  methods: {
    alert: function(event, items, listener) {
      this.left = event.clientX;
      this.top = event.clientY;
      this.hide = true;
      this.show = true;
      this.items = items;
      this.listener = listener;
      setTimeout(() => {
        var view = this.$refs.menuContainer;
        if (this.left + view.clientWidth > window.innerWidth) {
          this.left = Math.max(this.left - view.clientWidth, 0);
        }
        if (this.top + view.clientHeight > window.innerHeight) {
          this.top = Math.max(this.top - view.clientHeight, 0);
        }
        this.hide = false;
      });
    },
    close: function() {
      this.show = false;
      this.items = [];
      this.listener = null;
    },
    onMouseDown: function(event) {
      var intercept = this.show;
      var inner = this.$refs.menuContainer == event.target || getChildIndex(this.$refs.menuContainer, event.target) >= 0;
      if (!inner) {
        this.close();
      }
      return intercept;
    },
    onClick: function(event) {
      if (this.show) {
        var index = getChildIndex(this.$refs.menuContainer, event.target);
        if (index >= 0) {
          this.onClickItem(index);
        }
      }
    },
    onKeyDown: function(event) {
      return this.show;
    },
    onClickItem: function(index) {
      var enable = this.items[index][2];
      if (enable) {
        this.listener(index);
        this.close();
      }
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
  box-shadow: 0px 2px 6px @color-border-shadow;
  padding-top: 4px;
  padding-bottom: 4px;
  > div {
    padding-left: 12px;
    padding-right: 6px;
    line-height: 22px;
    display: flex;
    justify-content: space-between;
    > span:first-child {
      font-family: 'PingFang SC';
      font-size: 12px;
      color: @color-darker-text;
      margin-right: 47px;
    }
    > span:last-child {
      font-family: 'PingFang SC';
      font-size: 12px;
      color: @color-darker-text;
    }
  }
  > div[css-enable] {
    cursor: pointer;
    * {
      cursor: pointer;
    }
    > span:first-child {
      color: @color-menu-text;
    }
    > span:last-child {
      color: @color-menu-dark-text;
    }
  }
  > div[css-enable]:hover {
    background: @color-hover-background;
  }
}
</style>
