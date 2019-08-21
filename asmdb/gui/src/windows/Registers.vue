<template>
  <div class="registers-container">
    <Navigation :name="'Registers'" :disable="disable"></Navigation>
    <Gird :value="[{'id':1},{'id':2},{'id':3},{'id':4}]" #default="props">
      <div style="width:400px;font-size:16px;color:#fff;">{{props.item.id}}</div>
    </Gird>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      disable: true
    };
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.registers-container {
  height: 160px; //todo
}
</style>
