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
  created: function() {
    document.addEventListener('click', this.onDomClick, true);
    document.addEventListener('keydown', this.onDomKeyDown, true);
  },
  destroyed: function() {
    document.removeEventListener('click', this.onDomClick, true);
    document.removeEventListener('keydown', this.onDomKeyDown, true);
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
    dismiss: function() {
      this.showing = false;
    },
    onBlur: function() {
      this.dismiss();
    },
    onDomClick: function(event) {
      if (this.showing) {
        event.stopPropagation();
      }
    },
    onDomKeyDown: function(event) {
      if (this.showing) {
        event.stopPropagation();
      }
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
