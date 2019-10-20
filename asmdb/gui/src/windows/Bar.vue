<template>
  <div class="bar-container">
    <span class="bar-title">{{title}}</span>
    <span class="bar-grow"></span>
    <span class="bar-item" v-for="(item, index) in items" :key="index" @click="onClickItem(index)">{{item}}</span>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      title: 'com.example.app',
      items: ['next', 'step', 'cont', 'rlse']
    };
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
  height: 40px;
  display: flex;
  .bar-title {
    line-height: 40px;
    margin-left: 3px;
    padding: 0px 9px;
    font-size: 16px;
    color: @color-text;
    font-family: 'Wawati SC';
  }
  .bar-grow {
    flex-grow: 1;
  }
  .bar-item {
    line-height: 40px;
    padding: 0px 9px;
    font-size: 16px;
    color: @color-text;
    font-family: 'Wawati SC';
    cursor: pointer;
  }
  .bar-item:nth-last-child(1) {
    margin-right: 3px;
  }
  .bar-item:hover {
    color: @color-text-light;
  }
}
</style>
