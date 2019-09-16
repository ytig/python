<template>
  <div ref="container" class="pager-container"></div>
</template>

<script>
class Wheeling {
  constructor(handler) {
    this.handler = handler;
  }

  onWheel(event) {
    //todo
    console.log(event.cancelable);
  }
}

export default {
  data: function() {
    return {
      wheeling: new Wheeling(this)
    };
  },
  props: {
    canSub: Boolean,
    canAdd: Boolean
  },
  mounted: function() {
    this.$refs.container.parentNode.addEventListener('wheel', this.wheeling.onWheel);
  },
  destroyed: function() {
    this.$refs.container.parentNode.removeEventListener('wheel', this.wheeling.onWheel);
  },
  methods: {
    onWheelDown: function() {
      //todo
    },
    onWheelMove: function(dx, dy) {
      //todo
    },
    onWheelUp: function() {
      //todo
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.pager-container {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}
</style>
