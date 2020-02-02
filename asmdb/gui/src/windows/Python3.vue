<template>
  <div class="python3-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp" float>
    <Navigation2 class="python3-navigation2" :name="'python3'" :focus="focus" @mouseup2="onMouseUp2">
      <Resize class="python3-resize" :direction="'row'" :lowest="windowHeight==maxHeight" :uppest="windowHeight==minHeight" @dragstart2="onDragStart2" @drag2="onDrag2(-arguments[0])" @dragend2="onDragEnd2"></Resize>
    </Navigation2>
    <div class="python3-content" :style="{height:windowHeight+'px',paddingTop:paddingTop+'px',paddingBottom:paddingBottom+'px'}">
      <Terminal ref="terminal" class="python3-terminal" :focus="focus&&!$menu.show" :utf8="utf8"></Terminal>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
const WIDTH0 = 7;
const HEIGHT0 = 16;
const PADDING = 4;

export default {
  data: function() {
    return {
      minHeight: HEIGHT0 * 5 + (2 * PADDING - 2),
      maxHeight: HEIGHT0 * 20 + (2 * PADDING - 2),
      curHeight: 0,
      addHeight: 0,
      focus: false,
      utf8: '',
      counter: 0,
      size: null
    };
  },
  computed: {
    windowHeight: function() {
      return Math.min(Math.max(this.curHeight + this.addHeight, this.minHeight), this.maxHeight);
    },
    paddingTop: function() {
      return PADDING - 2 + ((this.windowHeight - (2 * PADDING - 2)) % HEIGHT0);
    },
    paddingBottom: function() {
      return PADDING;
    }
  },
  created: function() {
    var curHeight = loadStorage('python3_height', 0);
    this.curHeight = Math.min(Math.max(curHeight, this.minHeight), this.maxHeight);
    if (curHeight != this.curHeight) {
      saveStorage('python3_height', this.curHeight);
    }
  },
  mounted: function() {
    keyboard.registerWindow(this);
    asmdb.getInstance().registerEvent('python3', this);
    this.setWindowSize();
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('python3', this);
    keyboard.unregisterWindow(this);
  },
  methods: {
    requestFocus: function() {
      keyboard.requestFocus(this);
    },
    onFocusChanged: function(value) {
      this.focus = value;
    },
    onMouseUp: function(event) {
      if (event.button == 2) {
        this.onMouseUp2(event);
      }
    },
    onMouseUp2: function(evnet) {
      var items = [];
      items.push(['Clear all', '', true]);
      this.$menu.alert(event, items, this.onClickMenu);
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
          this.$refs.terminal.clearBy('>>> ');
          break;
      }
    },
    onKeyDown: function(event) {
      return false;
    },
    onRead: function(utf8) {
      this.utf8 = utf8;
    },
    smoothDragTo: function(to) {
      var from = this.curHeight;
      var duration = 147;
      var maxi = Math.ceil((duration * 3) / 50);
      var counter = this.counter;
      requestAnimationFrames(i => {
        if (counter != this.counter || this._isDestroyed) {
          return true;
        }
        var t = ++i / maxi;
        t = 1 - (1 - t) * (1 - t);
        this.curHeight = parseInt((1 - t) * from + t * to);
        return !(i < maxi);
      });
    },
    onDragStart2: function() {
      this.counter++;
      this.setWindowSize();
    },
    onDrag2: function(delta) {
      this.addHeight = delta;
      this.setWindowSize();
    },
    onDragEnd2: function(moved) {
      if (moved) {
        this.curHeight = this.windowHeight;
        this.addHeight = 0;
        saveStorage('python3_height', this.curHeight);
      } else {
        var newHeight = this.curHeight != this.minHeight ? this.minHeight : this.maxHeight;
        this.smoothDragTo(newHeight);
        this.setWindowSize(newHeight);
        saveStorage('python3_height', newHeight);
      }
    },
    setWindowSize(windowHeight) {
      if (windowHeight == undefined) {
        windowHeight = this.windowHeight;
      }
      var width = this.$el.clientWidth - 24;
      var height = windowHeight - (2 * PADDING - 2);
      var cols = parseInt(width / WIDTH0);
      var rows = parseInt(height / HEIGHT0);
      var size = cols + '*' + rows;
      if (this.size != size) {
        this.size = size;
        asmdb.getInstance().setwinsize(rows, cols);
        this.$refs.terminal.setWindowSize(rows, cols);
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.python3-container {
  .python3-resize {
    margin-top: 4px;
    height: 8px;
  }
  .python3-content {
    background: @color-background;
    .python3-terminal {
      height: 100%;
    }
  }
}
</style>
