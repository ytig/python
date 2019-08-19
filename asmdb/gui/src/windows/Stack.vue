<template>
  <div class="window">
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

.window {
  width: 360px; //todo
}
</style>
