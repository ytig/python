<template>
  <div class="terminal-container">
    <TerminalParent v-if="source!=null" class="terminal-parent" :source="source" #default="props">
      <TerminalChild :value="props.item.value" :styles="props.item.styles" :cursor="source.toCursor(props.index,focus)" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></TerminalChild>
    </TerminalParent>
  </div>
</template>

<script>
import resize from '@/scripts/resize';
import asmdb from '@/scripts/asmdb';
import TerminalParent from './Terminal_parent';
import TerminalChild from './Terminal_child';
const WIDTH0 = TerminalChild.WIDTH0;
const HEIGHT0 = TerminalChild.HEIGHT0;
//focus
//width height -> setwinsize
//linux bytes
//input -> writeb 粘贴，中文输入：悬浮
//scroll infinite
class Source {
  constructor() {
    this.width = 0;
    this.height = 0;
    this.length = 0;
    this[this.length++] = {
      value: '',
      styles: '[]',
      height: HEIGHT0
    };
    this.cursor = 0;
    this.background = '';
    this.color = '';
    this.invalidate = 0;
  }

  toCursor(index, focus) {
    if (index == this.length - 1) {
      return JSON.stringify([this.cursor, focus]);
    } else {
      return null;
    }
  }

  setwinsize(width, height) {
    if (this.width != width) {
      this.width = width;
      for (var i = 0; i < this.length; i++) {
        this[i].height = TerminalChild.measureHeight(this.width, this[i].value);
      }
      this.invalidate++;
    }
    if (this.height != height) {
      this.height = height;
    }
    asmdb.getInstance().setwinsize(parseInt(height / HEIGHT0), parseInt(width / WIDTH0));
  }

  readu(utf8) {
    for (var i = 0; i < utf8.length; i++) {
      console.log(utf8.charCodeAt(i), utf8.substring(i, i + 1));
    }
    var N = parseInt(this.width / WIDTH0);
    for (var item of this.splitu(utf8, /\x0a/, /\x0d/, /\x07/, /\x08/, /\x1b\[\d{0,}A/, /\x1b\[\d{0,}B/, /\x1b\[\d{0,}C/, /\x1b\[\d{0,}D/, /\x1b\[K/, /\x1b\[\d{0,}P/)) {
      var type = item[0];
      var value = item[1];
      switch (type) {
        case 0:
          this.insert(value);
          break;
        case 1:
          this.newline();
          break;
        case 2:
          this.cursor -= this.cursor % N;
          break;
        case 3:
          break;
        case 4:
          this.cursor--;
          break;
        case 5:
          var n = parseInt(value.substring(2, value.length - 1) | '1');
          this.cursor -= n * N;
          break;
        case 6:
          var n = parseInt(value.substring(2, value.length - 1) | '1');
          this.cursor += n * N;
          break;
        case 7:
          var n = parseInt(value.substring(2, value.length - 1) | '1');
          this.cursor += n;
          break;
        case 8:
          var n = parseInt(value.substring(2, value.length - 1) | '1');
          this.cursor -= n;
          break;
        case 9:
          this.delete();
          break;
        case 10:
          var n = parseInt(value.substring(2, value.length - 1) | '1');
          this.delete(n); //todo bug fix?
          break;
      }
    }
    this.invalidate++;
  }

  insert(value) {
    var current = this[this.length - 1];
    var cols = Math.ceil(TerminalChild.measureChar(value) / TerminalChild.measureChar(' '));
    var newValue = current.value.substring(0, this.cursor) + value + current.value.substring(this.cursor + cols);
    var newStyles = JSON.parse(current.styles);
    var insertStyles = [];
    for (var i = 0; i < value.length; i++) {
      insertStyles.push([this.background, this.color]);
    }
    newStyles.splice(this.cursor, cols, ...insertStyles);
    current.value = newValue;
    current.styles = JSON.stringify(newStyles);
    current.height = TerminalChild.measureHeight(this.width, newValue);
    this.cursor += value.length;
  }

  delete(n) {
    var current = this[this.length - 1];
    if (n == undefined) {
      n = current.value.length - this.cursor;
    }
    var newValue = current.value.substring(0, this.cursor) + current.value.substring(this.cursor + n);
    var newStyles = JSON.parse(current.styles);
    newStyles.splice(this.cursor, n);
    current.value = newValue;
    current.styles = JSON.stringify(newStyles);
    current.height = TerminalChild.measureHeight(this.width, newValue);
  }

  newline() {
    var current = this[this.length - 1];
    var N = parseInt(this.width / WIDTH0);
    var row = parseInt(this.cursor / N);
    if (row >= parseInt(current.height / HEIGHT0) - 1) {
      this[this.length++] = {
        value: '',
        styles: '[]',
        height: HEIGHT0
      };
      this.cursor = 0;
    } else {
      this.cursor = (row + 1) * N;
    }
  }

  splitu(utf8, ...patterns) {
    var result = [[0, utf8]];
    var type = 0;
    for (var pattern of patterns) {
      type++;
      var i = -1;
      while (++i < result.length) {
        if (result[i][0] != 0) {
          continue;
        }
        var text = result[i][1];
        var matcher = pattern.exec(text);
        if (!matcher) {
          continue;
        }
        result.splice(i, 1, [0, text.substring(0, matcher.index)], [type, matcher[0]], [0, text.substring(matcher.index + matcher[0].length)]);
      }
    }
    for (var i = result.length - 1; i >= 0; i--) {
      if (!result[i][1]) {
        result.splice(i, 1);
      }
    }
    return result;
  }
}

export default {
  components: {
    TerminalParent: TerminalParent,
    TerminalChild: TerminalChild
  },
  data: function() {
    return {
      source: null
    };
  },
  props: {
    focus: Boolean,
    utf8: String
  },
  watch: {
    utf8: {
      immediate: true,
      handler: function callee(newValue, oldValue) {
        if (this.$el == undefined) {
          this.$nextTick(callee.bind(this, ...arguments));
          return;
        }
        if (this.source == null) {
          this.source = new Source();
          this.onResize();
        }
        this.source.readu(oldValue == undefined ? newValue : newValue.substring(oldValue.length));
      }
    }
  },
  mounted: function() {
    resize.registerEvent(this);
  },
  destroyed: function() {
    resize.unregisterEvent(this);
  },
  methods: {
    onResize: function() {
      if (this.source != null) {
        this.source.setwinsize(this.$el.clientWidth - 24, this.$el.clientHeight);
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.terminal-container {
  .terminal-parent {
    margin: 0px 12px;
    height: 100%;
  }
}
</style>
