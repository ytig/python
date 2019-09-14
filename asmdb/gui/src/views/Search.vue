<template>
  <div v-show="showing" class="search-container">
    <input ref="input" type="text" v-model="text" @blur="onBlur" />
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      showing: false,
      text: ''
    };
  },
  updated: function() {
    var input = this.$refs.input;
    if (this.showing) {
      input.focus();
    }
  },
  methods: {
    show: function() {
      this.showing = true;
      this.text = '';
    },
    onBlur: function() {
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
