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
    getEventIndex(event) {
      return new Array(...this.$refs.menuContainer.childNodes).indexOf(event.target);
    },
    onMouseDown: function(event) {
      var intercept = this.show;
      if (this.getEventIndex(event) == -1) {
        this.close();
      }
      return intercept;
    },
    onClick: function(event) {
      if (this.show) {
        var index = this.getEventIndex(event);
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
  > div {
    font-size: 18px;
    background: #fff;
  }
}
</style>
