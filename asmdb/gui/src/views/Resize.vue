<template>
  <div class="resize-container" :css-direction="direction"></div>
</template>

<script>
function setGlobalCursor(style) {
  style = style || 'default';
  var cursor = document.getElementById('__cursor__');
  if (!cursor) {
    cursor = document.createElement('div');
    cursor.id = '__cursor__';
    cursor.style.position = 'fixed';
    cursor.style.left = '0px';
    cursor.style.top = '0px';
    cursor.style.width = '100%';
    cursor.style.height = '100%';
    cursor.style.zIndex = '999';
    document.body.appendChild(cursor);
  }
  cursor.style.cursor = style;
  cursor.style.display = style == 'default' ? 'none' : '';
}

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
    window.addEventListener('mousedown', this.onMouseDown);
    window.addEventListener('mousemove', this.onMouseMove);
    window.addEventListener('mouseup', this.onMouseUp);
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
        if (this.direction == 'col') {
          setGlobalCursor('col-resize');
        }
        if (this.direction == 'row') {
          setGlobalCursor('row-resize');
        }
      }
    },
    onMouseMove: function(event) {
      if (this.draging) {
        var deltaX = this.clientX - event.clientX;
        var deltaY = this.clientY - event.clientY;
        this.clientX = event.clientX;
        this.clientY = event.clientY;
        if (this.direction == 'col') {
          this.$emit('drag2', deltaX);
        }
        if (this.direction == 'row') {
          this.$emit('drag2', deltaY);
        }
      }
    },
    onMouseUp: function(event) {
      if (event.button == 0) {
        if (this.draging) {
          this.draging = false;
          setGlobalCursor(null);
        }
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
