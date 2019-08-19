<template>
  <div class="window">
    <i-title :name="'Memory'"></i-title>
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
  width: 530px; //todo
}
</style>
