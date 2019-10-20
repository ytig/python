<template>
  <div class="bar-container">
    <span class="bar-title">{{title}}</span>
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
  > span {
    line-height: 40px;
    padding: 0px 9px;
    font-size: 16px;
    color: @color-text;
    font-family: 'Wawati SC';
  }
  .bar-title {
    margin-left: 3px;
    flex-grow: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    contain: size;
  }
  .bar-item {
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
