<template>
  <div class="python3-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp" float>
    <Navigation2 class="python3-navigation2" :name="'python3'" :focus="focus" @mouseup2="onMouseUp2">
      <Resize class="python3-resize" :direction="'row'" :lowest="windowHeight==maxHeight" :uppest="windowHeight==minHeight" @dragstart2="onDragStart2" @drag2="onDrag2(-arguments[0])" @dragend2="onDragEnd2"></Resize>
    </Navigation2>
    <Terminal class="python3-terminal" :style="{height:windowHeight+'px'}" :focus="focus" :utf8="utf8"></Terminal>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import resize from '@/scripts/resize';
import asmdb from '@/scripts/asmdb';

export default {
  data: function() {
    return {
      minHeight: 16 * 5 + 6,
      maxHeight: 16 * 20 + 6,
      curHeight: 0,
      addHeight: 0,
      focus: false,
      utf8: '',
      counter: 0
    };
  },
  watch: {
    windowHeight: function() {
      this.$nextTick(resize.dispatchEvent);
    }
  },
  computed: {
    windowHeight: function() {
      return Math.min(Math.max(this.curHeight + this.addHeight, this.minHeight), this.maxHeight);
    }
  },
  created: function() {
    var curHeight = loadStorage('python3_height', 0);
    this.curHeight = Math.min(Math.max(curHeight, this.minHeight), this.maxHeight);
  },
  mounted: function() {
    keyboard.registerWindow(this);
    asmdb.getInstance().registerEvent('python3', this);
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
      this.$menu.alert(event);
    },
    onKeyDown: function(event) {
      //for test
      switch (event.key) {
        case 'Enter':
          asmdb.getInstance().writeu('\n');
          break;
        case 'Backspace':
          asmdb.getInstance().writeu('\x08');
          break;
        case 'Tab':
          asmdb.getInstance().writeu('\x09');
          break;
        case 'ArrowLeft':
          asmdb.getInstance().writeu('\x02');
          break;
        case 'ArrowRight':
          asmdb.getInstance().writeu('\x06');
          break;
        case 'ArrowUp':
          asmdb.getInstance().writeu('\x10');
          break;
        case 'ArrowDown':
          asmdb.getInstance().writeu('\x0e');
          break;
        case 'Alt':
        case 'Control':
        case 'Meta':
        case 'Shift':
          return false;
        default:
          if (event.altKey || event.ctrlKey || event.metaKey) {
            return false;
          }
          asmdb.getInstance().writeu(event.key);
          break;
      }
      return true;
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
        if (counter != this.counter) {
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
    },
    onDrag2: function(delta) {
      this.addHeight = delta;
    },
    onDragEnd2: function(moved) {
      if (moved) {
        this.curHeight = this.windowHeight;
        this.addHeight = 0;
        saveStorage('python3_height', this.curHeight);
      } else {
        var newHeight = this.curHeight != this.minHeight ? this.minHeight : this.maxHeight;
        this.smoothDragTo(newHeight);
        saveStorage('python3_height', newHeight);
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
  .python3-terminal {
    width: 94px; //for test
    background: @color-background;
  }
}
</style>
