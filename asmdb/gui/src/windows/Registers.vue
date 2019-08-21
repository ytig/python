<template>
  <div class="registers-container">
    <Navigation :name="'Registers'" :disable="disable"></Navigation>
    <Gird :items="items" #default="props">
      <div style="width:400px;font-size:12px;color:#fff;">{{props.item.id}}</div>
    </Gird>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      disable: true,
      items: []
    };
  },
  created: function() {
    var i;
    for (i = 0; i < 17; i++) {
      this.items.splice(0, 0, { id: i }); //test
    }
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.registers-container {
}
</style>
