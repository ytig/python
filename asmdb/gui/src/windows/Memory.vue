<template>
  <div class="memory-container">
    <Navigation :name="'Memory'" :disable="true"></Navigation>
    <Bytes :value="{lineNumber:'0x00112233',newBytes:[1,2,3,4,5,6,7,8,1,2,3,4,5,6,7,8],showString:true}"></Bytes>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      disable: true
    };
  }
};
</script>

<style lang="less">
@import '~@/styles/theme.less';

.memory-container {
}
</style>
