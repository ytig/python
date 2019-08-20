<template>
  <div class="stack-container">
    <Title :name="'Stack'"></Title>
    <div v-for="i in Array(39)" :key="i">
      <div class="todo">+0x190 &nbsp;00 01 02 03 04 05 06 07</div>
    </div>
    <div class="indicator">
      <div v-for="(item, index) in Array(10)" :key="index">{{index}}</div>
    </div>
  </div>
</template>

<script>
export default {};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.stack-container {
  display: flex;
  flex-direction: column;
  .todo {
    padding: 0px 12px;
    color: #abb2bf;
    font-size: 12px;
  }
  .indicator {
    flex-grow: 1;
    display: flex;
    align-items: flex-end;
    > *:first-child {
      border-left: 0px;
    }
    > * {
      flex-grow: 1;
      height: 40px;
      line-height: 40px;
      background: @color-dark-background;
      border-top: 1px solid @color-border;
      border-left: 1px solid @color-border;
      text-align: center;
      color: #abb2bf;
      font-size: 12px;
    }
  }
}
</style>
