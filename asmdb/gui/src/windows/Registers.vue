<template>
  <div class="registers-container">
    <Navigation :name="'Registers'" :disable="disable"></Navigation>
    <Gird :column="3" :items="items" #default="props">
      <span style="font-size:12px;color:#abb2bf;">{{props.item.id}} 0xaabbccdd 123</span>
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
