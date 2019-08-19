<template>
  <div class="container">
    <i-title :name="'Registers'"></i-title>
  </div>
</template>

<script>
import iTitle from "@/views/Title";

export default {
  name: "Registers",
  components: {
    "i-title": iTitle
  }
};
</script>

<style lang="less" scoped>
@import "~@/styles/global.less";

.container {
  height: 160px; //todo
}
</style>
