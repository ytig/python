<template>
  <div class="stack-container">
    <Navigation :name="'Stack'"></Navigation>
    <div v-for="i in Array(39)" :key="i">
      <div class="todo">+0x190 &nbsp;00 01 02 03 04 05 06 07</div>
    </div>
    <div class="stack-fill"></div>
    <Indicator :size="10" v-model="page" :disable="disable"></Indicator>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      disable: true,
      page: 0
    };
  }
};
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
  .stack-fill {
    flex-grow: 1;
  }
}
</style>
