<template>
  <div :style="{cursor:cursor}"></div>
</template>

<script>
function setGlobalCursor(style) {
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
  if (style) {
    cursor.style.cursor = style;
    cursor.style.display = '';
  } else {
    cursor.style.display = 'none';
  }
}

export default {
  data: function() {
    return {
      draging: false,
      downT: 0,
      downX: 0,
      downY: 0,
      moved: false
    };
  },
  props: {
    direction: String,
    lowest: Boolean,
    uppest: Boolean
  },
  computed: {
    cursor: function() {
      var cursor = 'default';
      if (this.direction == 'col') {
        if (!this.lowest && !this.uppest) {
          cursor = 'ew-resize';
        }
        if (this.lowest && !this.uppest) {
          cursor = 'e-resize';
        }
        if (!this.lowest && this.uppest) {
          cursor = 'w-resize';
        }
      }
      if (this.direction == 'row') {
        if (!this.lowest && !this.uppest) {
          cursor = 'ns-resize';
        }
        if (this.lowest && !this.uppest) {
          cursor = 's-resize';
        }
        if (!this.lowest && this.uppest) {
          cursor = 'n-resize';
        }
      }
      if (this.draging) {
        setGlobalCursor(cursor);
      }
      return cursor;
    }
  },
  created: function() {
    window.addEventListener('mousedown', this.onMouseDown);
    window.addEventListener('mousemove', this.onMouseMove);
    window.addEventListener('mouseup', this.onMouseUp);
  },
  beforeDestroy: function() {
    this.onMouseUp({ button: 0 });
  },
  destroyed: function() {
    window.removeEventListener('mousedown', this.onMouseDown);
    window.removeEventListener('mousemove', this.onMouseMove);
    window.removeEventListener('mouseup', this.onMouseUp);
  },
  methods: {
    onMouseDown: function(event) {
      if (event.button == 0 && event.target == this.$el) {
        this.draging = true;
        this.downT = new Date().getTime();
        this.downX = event.clientX;
        this.downY = event.clientY;
        this.moved = false;
        setGlobalCursor(this.cursor);
        this.$emit('dragstart2');
      }
    },
    onMouseMove: function(event) {
      if (this.draging) {
        this.moved = true;
        if (this.direction == 'col') {
          this.$emit('drag2', event.clientX - this.downX);
        }
        if (this.direction == 'row') {
          this.$emit('drag2', event.clientY - this.downY);
        }
      }
    },
    onMouseUp: function(event) {
      if (event.button == 0) {
        if (this.draging) {
          this.draging = false;
          setGlobalCursor(null);
          this.$emit('dragend2', this.moved || new Date().getTime() - this.downT >= 224);
        }
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';
</style>
