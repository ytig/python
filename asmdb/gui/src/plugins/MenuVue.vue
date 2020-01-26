<template>
  <div ref="container" v-show="show" class="menu-container" :style="{left:left+'px',top:top+'px'}">
    <div v-for="(item, index) in items" :key="index" :css-enable="item[2]">
      <span class="user-select-none">{{item[0]}}</span>
      <span v-show="item[1].length>0" class="user-select-none">{{item[1]}}</span>
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
      show: false,
      items: [],
      listener: null
    };
  },
  methods: {
    alert: function(event, items, listener) {
      this.left = 0;
      this.top = 0;
      this.show = true;
      this.items = items || [['nothing', '', false]];
      this.listener = listener || null;
      this.$nextTick(() => {
        var view = this.$refs.container;
        this.left = event.clientX - (event.clientX + view.clientWidth <= window.innerWidth ? 0 : view.clientWidth);
        this.top = event.clientY - (event.clientY + view.clientHeight <= window.innerHeight ? 0 : view.clientHeight);
      });
    },
    close: function() {
      this.show = false;
      this.items = [];
      this.listener = null;
    },
    onMouseDown: function(event) {
      var intercept = this.show;
      var inner = this.$refs.container == event.target || getChildIndex(this.$refs.container, event.target) >= 0;
      if (!inner) {
        this.close();
      }
      return intercept;
    },
    onClick: function(event) {
      if (this.show) {
        var index = getChildIndex(this.$refs.container, event.target);
        if (index >= 0) {
          this.onClickItem(index);
        }
      }
    },
    onKeyDown: function(event) {
      return this.show;
    },
    onWheel: function(event) {
      this.close();
      return false;
    },
    onClickItem: function(index) {
      var enable = this.items[index][2];
      if (enable) {
        this.listener && this.listener(index);
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
  z-index: 7;
  display: inline-block;
  background: @color-background-dark;
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
      color: @color-text-darker;
      margin-right: 24px;
    }
    > span:last-child {
      font-family: 'PingFang SC';
      font-size: 12px;
      color: @color-text-darker;
      margin-left: 24px;
    }
  }
  > div[css-enable] {
    cursor: pointer;
    * {
      cursor: pointer;
    }
    > span:first-child {
      color: @color-text-menu;
    }
    > span:last-child {
      color: @color-text-menu-dark;
    }
  }
  > div[css-enable]:hover {
    background: @color-background-hover;
  }
}
</style>
