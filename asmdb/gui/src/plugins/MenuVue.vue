<template>
  <div ref="menuContainer" v-show="show" class="menu-container">
    <div v-for="(item, index) in items" :key="index">{{item}}</div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      show: false,
      items: []
    };
  },
  methods: {
    alert: function(items) {
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
  left: 0px;
  top: 0px;
  // width: 100%;
  // height: 100%;
  > div {
    font-size: 18px;
    background: #fff;
  }
}
</style>
