<template>
  <div class="window">
    <i-title :name="'Watchpoints'"></i-title>
  </div>
</template>

<script>
import iTitle from "@/views/Title";

export default {
  name: "Watchpoints",
  components: {
    "i-title": iTitle
  }
};
</script>

<style lang="less" scoped>
@import "~@/styles/global.less";

.window {
  width: 160px; //todo
  height: 160px; //todo
}
</style>
