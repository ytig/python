<template>
  <div class="bar-container">
    <div></div>
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
  > div {
    margin-left: 12px;
    margin-top: 10px;
    width: 20px;
    height: 20px;
    mask-image: url('~@/icons/title.png');
    background: @color-text;
  }
  > span {
    line-height: 40px;
    font-size: 16px;
    color: @color-text;
    font-family: 'Wawati SC';
  }
  .bar-title {
    width: 0px;
    flex-grow: 1;
    margin-left: 6px;
    margin-right: 3px;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
  .bar-item {
    padding: 0px 9px;
    cursor: pointer;
  }
  .bar-item:hover {
    color: @color-text-light;
  }
  > span:nth-last-of-type(1) {
    margin-right: 3px;
  }
}
</style>
