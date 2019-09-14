<template>
  <div v-show="showing" class="search-container">
    <input ref="input" type="text" @blur="onBlur" />
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      showing: false
    };
  },
  updated: function() {
    if (this.showing) {
      this.$refs.input.focus();
    }
  },
  methods: {
    show: function() {
      this.showing = true;
    },
    onBlur: function(event) {
      this.showing = false;
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.search-container {
  position: fixed;
  width: 100px;
  height: 32px;
  > input {
    font-size: 12px;
  }
}
</style>
