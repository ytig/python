<template>
  <div v-show="show" class="menu-container">
    <div v-for="(item, index) in items" :key="index">{{item}}</div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      show: Boolean,
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
    onMouseDown: function(event) {
      var intercept = this.show;
      if (true) {
        //todo outside dismiss
        this.close();
      }
      return intercept;
    },
    onClick: function(event) {
      if (this.show) {
        //todo check click position
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
