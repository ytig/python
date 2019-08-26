<template>
  <div ref="menuContainer" v-show="show" class="menu-container" :style="{left:left+'px',top:top+'px'}">
    <div v-for="(item, index) in items" :key="index">{{item}}</div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      left: 0,
      top: 0,
      show: false,
      items: []
    };
  },
  methods: {
    alert: function(event, items) {
      this.left = event.clientX;
      this.top = event.clientY;
      this.show = true;
      this.items = items;
    },
    close: function() {
      this.show = false;
      this.items = [];
    },
    onMouseDown: function(event) {
      var intercept = this.show;
      var outside = true;
      var el = event.target;
      while (el) {
        if (el == this.$refs.menuContainer) {
          outside = false;
          break;
        }
        el = el.parentNode;
      }
      if (outside) {
        this.close();
      }
      return intercept;
    },
    onClick: function(event) {
      if (this.show) {
        var index = new Array(...this.$refs.menuContainer.childNodes).indexOf(event.target);
        if (index >= 0) {
          this.onClickItem(index);
        }
      }
    },
    onKeyDown: function(event) {
      return this.show;
    },
    onClickItem: function(index) {
      console.log(index);
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
  background: #21252b;
  box-shadow: 0px 0px 6px @color-border-shadow;
  padding-top: 4px;
  padding-bottom: 4px;
  min-width: 147px;
  > div {
    padding-left: 12px;
    padding-right: 12px;
    line-height: 22px;
    font-size: 12px;
    color: @color-text;
  }
  > div:hover {
    background: #383e4a;
  }
}
</style>
