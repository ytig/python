<template>
  <div v-show="show" class="menu-container" @click="close">
    <div class="menu-layout">
      <div v-for="(item, index) in items" :key="index" @click="clickItem(index);$event.stopPropagation();">{{item}}</div>
    </div>
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
    clickItem: function(index) {
      //emit
      this.close();
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.menu-container {
  position: fixed;
  left: 0px;
  top: 0px;
  width: 100%;
  height: 100%;
  .menu-layout {
    display: inline-block;
    > div {
      font-size: 18px;
      background: #fff;
    }
  }
}
</style>
