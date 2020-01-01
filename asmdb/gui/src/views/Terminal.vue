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

function splitu(utf8, ...patterns) {
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

class Word {
  constructor(value, ...styles) {
    this.value = value;
    this.styles = styles;
  }
}

class Line {
  constructor(width) {
    this.width = width;
    this.words = [];
    this.invalidate();
  }

  invalidate() {
    var value = '';
    var styles = [];
    for (var word of this.words) {
      value += word.value;
      styles.push(word.styles);
    }
    this.value = value;
    this.styles = JSON.stringify(styles);
    this.height = TerminalChild.measureHeight(this.width, this.value);
  }

  onResize(width) {
    this.width = width;
    this.invalidate();
  }
}

class Source {
  constructor(width, height) {
    this.width = width;
    this.height = height;
    this.length = 0;
    this[this.length++] = new Line(this.width);
    this.index = 0;
    this.offset = 0;
    this.background = '';
    this.color = '';
    this.invalidate = 0;
    this.setwinsize();
  }

  toCursor(index, focus) {
    if (index == this.index) {
      return JSON.stringify([this.offset, focus]);
    } else {
      return null;
    }
  }

  onResize(width, height) {
    var changed = false;
    if (this.width != width) {
      this.width = width;
      changed = true;
      for (var i = 0; i < this.length; i++) {
        this[i].onResize(width);
      }
      this.invalidate++;
    }
    if (this.height != height) {
      this.height = height;
      changed = true;
    }
    if (changed) {
      this.setwinsize();
    }
  }

  setwinsize() {
    asmdb.getInstance().setwinsize(parseInt(this.height / HEIGHT0), parseInt(this.width / WIDTH0));
  }

  router = {
    lf: /\x0a/,
    cr: /\x0d/,
    bel: /\x07/,
    bs: /\x08/,
    escA: /\x1b\[\d{0,}A/,
    escB: /\x1b\[\d{0,}B/,
    escC: /\x1b\[\d{0,}C/,
    escD: /\x1b\[\d{0,}D/,
    escK: /\x1b\[K/,
    escP: /\x1b\[\d{0,}P/
  };

  input(utf8) {
    for (var char of utf8) {
      var w = TerminalChild.measureChar(char) / WIDTH0;
      //todo fix
      this[this.index].words.splice(this.offset, 1, new Word(char, this.background, this.color));
      this[this.index].invalidate();
      this.offset++;
    }
  }

  lf() {
    var N = parseInt(this.width / WIDTH0);
    var row = this[this.index].height / HEIGHT0;
    if (this.offset + N < row * N) {
      this.offset += N - (this.offset % N);
    } else {
      if (this.index == this.length - 1) {
        this[this.length++] = new Line(this.width);
      }
      this.index++;
      this.offset = 0;
    }
  }

  cr() {
    var N = parseInt(this.width / WIDTH0);
    this.offset -= this.offset % N;
  }

  bel() {}

  bs() {
    this.escD('\x1b[D');
  }

  escA(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) | '1');
    var N = parseInt(this.width / WIDTH0);
    for (var i = 0; i < n; i++) {
      if (this.offset - N >= 0) {
        this.offset -= N;
      }
    }
  }

  escB(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) | '1');
    var N = parseInt(this.width / WIDTH0);
    var row = this[this.index].height / HEIGHT0;
    for (var i = 0; i < n; i++) {
      if (this.offset + N < row * N) {
        this.offset += N;
      }
    }
  }

  escC(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) | '1');
    var N = parseInt(this.width / WIDTH0);
    for (var i = 0; i < n; i++) {
      if (this.offset % N != N - 1) {
        this.offset++;
      }
    }
  }

  escD(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) | '1');
    var N = parseInt(this.width / WIDTH0);
    for (var i = 0; i < n; i++) {
      if (this.offset % N != 0) {
        this.offset--;
      }
    }
  }

  escK() {
    //todo fix
    var N = parseInt(this.width / WIDTH0);
    this[this.index].words.splice(this.offset, 999);
    this[this.index].invalidate();
  }

  escP(utf8) {
    this.escK(); //todo fix
    // var n = parseInt(utf8.substring(2, utf8.length - 1) | '1');
  }

  readu(utf8) {
    for (var char of utf8) {
      console.log(char.charCodeAt(0), char);
    }
    var keys = [];
    var values = [];
    for (var key in this.router) {
      keys.push(key);
      values.push(this.router[key]);
    }
    keys.splice(0, 0, 'input');
    for (var item of splitu(utf8, ...values)) {
      this[keys[item[0]]](item[1]);
    }
    this.invalidate++;
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
          this.source = new Source(this.$el.clientWidth - 24, this.$el.clientHeight);
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
        this.source.onResize(this.$el.clientWidth - 24, this.$el.clientHeight);
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
