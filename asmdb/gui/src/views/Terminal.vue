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
    this.row = 0;
    this.col = 0;
    this.background = '';
    this.color = '';
    this.invalidate = 0;
    this.setwinsize();
  }

  toCursor(index, focus) {
    var COL = parseInt(this.width / WIDTH0);
    if (index == this.index) {
      return JSON.stringify([this.row, Math.min(this.col, COL - 1), focus]);
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

  word(char = '\u200b') {
    if (char == '\u200b') {
      return new Word(char, '', '');
    } else {
      return new Word(char, this.background, this.color);
    }
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
    var COL = parseInt(this.width / WIDTH0);
    for (var char of utf8) {
      var width = TerminalChild.measureChar(char) / WIDTH0;
      if (width == 1) {
        var index = 0;
        var offset = 0;
        var eof = this[this.index].words.length > 0 ? -1 : 0;
        var c = 0;
        while (c++ < this.row * COL + this.col) {
          if (eof >= 0) {
            eof++;
          } else {
            var w = TerminalChild.measureChar(this[this.index].words[index].value) / WIDTH0;
            offset++;
            if (offset >= w) {
              if (index + 1 < this[this.index].words.length) {
                index++;
                w = TerminalChild.measureChar(this[this.index].words[index].value) / WIDTH0;
                if (w == 1) {
                  offset = 0;
                } else {
                  if (c % COL != COL - 1) {
                    offset = 0;
                  } else {
                    offset = -1;
                  }
                }
              } else {
                eof = 0;
              }
            }
          }
        }
        if (eof >= 0) {
          for (var i = 0; i < eof; i++) {
            this[this.index].words.push(this.word());
          }
          this[this.index].words.push(this.word(char));
        } else {
          var w = TerminalChild.measureChar(this[this.index].words[index].value) / WIDTH0;
          if (offset >= 0) {
            if (w == 1) {
              this[this.index].words.splice(index, 1, this.word(char));
            } else {
              if (offset == 0) {
                this[this.index].words.splice(index, 1, this.word(char), this.word());
              } else {
                this[this.index].words.splice(index, 1, this.word(), this.word(char));
              }
            }
          } else {
            this[this.index].words.splice(index, 0, this.word(char));
          }
        }
        this[this.index].invalidate();
        if (this.col < COL) {
          this.col++;
        } else {
          this.row++;
          this.col = 1;
        }
      } else {
        //todo w=2
      }
    }
  }

  lf() {
    var ROW = this[this.index].height / HEIGHT0;
    if (this.row + 1 < ROW) {
      this.row++;
      this.col = 0;
    } else {
      if (this.index == this.length - 1) {
        this[this.length++] = new Line(this.width);
      }
      this.index++;
      this.row = 0;
      this.col = 0;
    }
  }

  cr() {
    this.col = 0;
  }

  bel() {
    playSound('/static/sounds/bel.m4a');
  }

  bs() {
    this.escD('\x1b[D');
  }

  escA(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) | '1');
    for (var i = 0; i < n; i++) {
      if (this.row - 1 >= 0) {
        this.row--;
      }
    }
  }

  escB(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) | '1');
    var ROW = this[this.index].height / HEIGHT0;
    for (var i = 0; i < n; i++) {
      if (this.row + 1 < ROW) {
        this.row++;
      }
    }
  }

  escC(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) | '1');
    var COL = parseInt(this.width / WIDTH0);
    for (var i = 0; i < n; i++) {
      if (this.col + 1 <= COL) {
        this.col++;
      }
    }
  }

  escD(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) | '1');
    for (var i = 0; i < n; i++) {
      if (this.col - 1 >= 0) {
        this.col--;
      }
    }
  }

  escK() {
    //todo fix
    var COL = parseInt(this.width / WIDTH0);
    var words = [];
    for (var i = 0; i < COL - this.col; i++) {
      words.push(this.word());
    }
    this[this.index].words.splice(this.row * COL + this.col, words.length, ...words);
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
