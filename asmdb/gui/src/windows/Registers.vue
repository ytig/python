<template>
  <div class="registers-container">
    <Title :name="'Registers'"></Title>
    <Gird :value="[{'id':1},{'id':2},{'id':3},{'id':4}]" #default="props">
      <div style="width:400px;font-size:16px;color:#fff;">{{props.item.id}}</div>
    </Gird>
  </div>
</template>

<script>
export default {};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.registers-container {
  height: 160px; //todo
}
</style>
