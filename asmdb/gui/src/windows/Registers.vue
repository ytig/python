<template>
  <div class="registers-container">
    <Navigation :name="'Registers'" :disable="disable"></Navigation>
    <Gird :column="4" :items="items" #default="props">
      <div style="width:100%;font-size:12px;color:#abb2bf;text-align:center;">{{props.item.id}} 0xaabbccdd 123</div>
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
