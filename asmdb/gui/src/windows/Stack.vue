<template>
  <div class="container">
    <i-title :name="'Stack'"></i-title>
  </div>
</template>

<script>
import iTitle from "@/views/Title";

export default {
  name: "Stack",
  components: {
    "i-title": iTitle
  }
};
</script>

<style lang="less" scoped>
@import "~@/styles/global.less";

.container {
  width: 360px; //todo
}
</style>
