<template>
  <div class="bar-container">
    <div class="bar-icon"></div>
    <span class="bar-text">{{title}}</span>
    <div class="bar-item" v-for="(item, index) in items" :key="index" :style="item" @click="onClickItem(index)" :css-enable="enable"></div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      enable: false,
      title: 'com.example.app'
    };
  },
  computed: {
    items: function() {
      var items = [];
      for (var icon of ['next', 'step', 'cont', 'rlse']) {
        var url = "url('/static/icons/" + icon + ".png'";
        if (this.enable) {
          items.push({ backgroundImage: url });
        } else {
          items.push({ maskImage: url });
        }
      }
      return items;
    }
  },
  methods: {
    onClickItem: function(index) {
      //todo
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.bar-container {
  height: 32px;
  display: flex;
  .bar-icon {
    margin-left: 3px;
    width: 32px;
    height: 32px;
    background-size: 22px 22px;
    background-repeat: no-repeat;
    background-position: center center;
    background-image: url('/static/icons/android.png');
  }
  .bar-text {
    margin-right: 3px;
    width: 0px;
    flex-grow: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    line-height: 32px;
    font-size: 16px;
    color: @color-text;
    font-family: 'Wawati SC';
  }
  .bar-item {
    width: 32px;
    height: 32px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    mask-size: 16px 16px;
    mask-repeat: no-repeat;
    mask-position: center center;
    background-color: @color-text-dark;
    cursor: not-allowed;
  }
  .bar-item[css-enable] {
    background-color: transparent;
    cursor: pointer;
  }
  .bar-item[css-enable]:hover {
    border: 4px solid @color-background-dark;
    border-radius: 4px;
    background-color: @color-background-hover;
  }
  .bar-item:last-child {
    margin-right: 3px;
  }
}
</style>
