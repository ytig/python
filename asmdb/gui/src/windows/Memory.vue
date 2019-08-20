<template>
  <div class="window">
    <i-title :name="'Memory'"></i-title>
    <span class="todo">0xbf001234 00 01 02 03 04 05 06 07 08 09 0a 0b 0c 0d 0e 0f ........aaaaaaaa</span>
  </div>
</template>

<script>
import iTitle from "@/views/Title";

export default {
  name: "Memory",
  components: {
    "i-title": iTitle
  }
};
</script>

<style lang="less" scoped>
@import "~@/styles/global.less";

.window {
  .todo {
    color: #abb2bf;
    font-size: 14px;
  }
}
</style>
