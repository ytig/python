<template>
  <div class="resize-container" :css-direction="direction"></div>
</template>

<script>
export default {
  data: function() {
    return {
      draging: false,
      clientX: 0,
      clientY: 0
    };
  },
  props: {
    direction: String
  },
  created: function() {
    document.addEventListener('mousedown', this.onMouseDown);
    document.addEventListener('mousemove', this.onMouseMove);
    document.addEventListener('mouseup', this.onMouseUp);
  },
  destroyed: function() {
    document.removeEventListener('mousedown', this.onMouseDown);
    document.removeEventListener('mousemove', this.onMouseMove);
    document.removeEventListener('mouseup', this.onMouseUp);
  },
  methods: {
    onMouseDown: function(event) {
      if (event.button == 0 && event.target == this.$el) {
        this.draging = true;
        this.clientX = event.clientX;
        this.clientY = event.clientY;
      }
    },
    onMouseMove: function(event) {
      if (this.draging) {
        var deltaX = this.clientX - event.clientX;
        var deltaY = this.clientY - event.clientY;
        if (this.direction == 'col') {
          this.$emit('drag2', deltaX);
        }
        if (this.direction == 'row') {
          this.$emit('drag2', deltaY);
        }
        this.clientX = event.clientX;
        this.clientY = event.clientY;
      }
    },
    onMouseUp: function(event) {
      if (event.button == 0) {
        this.draging = false;
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.resize-container[css-direction='col'] {
  cursor: col-resize;
}
.resize-container[css-direction='row'] {
  cursor: row-resize;
}
</style>
