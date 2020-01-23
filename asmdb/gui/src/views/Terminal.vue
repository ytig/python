<template>
  <div class="terminal-container">
    <TerminalParent ref="parent" v-if="source!=null" class="terminal-parent" :lineHeight="lineHeight" :source="source" @scroll2="onScroll2" #default="props">
      <TerminalChild :value="props.item.value" :styles="props.item.styles" :cursor="source.toCursor(props.index,focus)" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></TerminalChild>
    </TerminalParent>
    <TerminalInput class="terminal-input" :style="{left:inputLeft+'px',top:inputTop+'px'}" :focus="focus" @input="onInput"></TerminalInput>
  </div>
</template>

<script>
import asmdb from '@/scripts/asmdb';
import resize from '@/scripts/resize';
import Theme from '@/styles/theme';
import TerminalParent from './Terminal_parent';
import TerminalChild from './Terminal_child';
import TerminalInput from './Terminal_input';
const COLORS = [Theme.colorBackground, Theme.colorText2, Theme.colorText5, Theme.colorText4, Theme.colorText3, Theme.colorBackgroundPopup2, Theme.colorBackgroundPopup, Theme.colorText];
const WIDTH0 = 7;
const HEIGHT0 = 16;

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
    this.limit = 0;
    this.invalidate();
  }

  position(cursor) {
    if (cursor >= this.limit) {
      return {
        index: null,
        offset: null,
        eof: cursor - this.limit
      };
    }
    var COL = parseInt(this.width / WIDTH0);
    var index = 0;
    var offset = 0;
    var c = 0;
    while (c++ < cursor) {
      var w = TerminalChild.measureChar(this.words[index].value) / WIDTH0;
      offset++;
      if (offset >= w) {
        index++;
        w = TerminalChild.measureChar(this.words[index].value) / WIDTH0;
        if (w == 1) {
          offset = 0;
        } else {
          if (c % COL != COL - 1) {
            offset = 0;
          } else {
            offset = -1;
          }
        }
      }
    }
    return {
      index: index,
      offset: offset,
      eof: null
    };
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
    this.lineCount = TerminalChild.measureHeight(this.width, value) / HEIGHT0;
  }
}

class Source {
  constructor(width) {
    this.width = width;
    this.length = 0;
    this[this.length++] = new Line(this.width);
    this.index = 0;
    this.row = 0;
    this.col = 0;
    this.bright = false;
    this.underline = false;
    this.flash = false;
    this.inverse = false;
    this.invisable = false;
    this.color = '';
    this.background = '';
    this.invalidate = 0;
  }

  getOffset(position, index) {
    var offset = 0;
    if (position.index >= index) {
      for (var i = index; i < position.index; i++) {
        offset -= this[i].lineCount;
      }
    } else {
      for (var i = position.index; i < index; i++) {
        offset += this[i].lineCount;
      }
    }
    return offset - position.offset;
  }

  getCursor(position) {
    var COL = parseInt(this.width / WIDTH0);
    var left = 12 + Math.min(this.col, COL - 1) * WIDTH0;
    var top = 1 + (this.getOffset(position, this.index) + this.row) * HEIGHT0;
    return [left, top];
  }

  toCursor(index, focus) {
    var COL = parseInt(this.width / WIDTH0);
    if (index == this.index) {
      return JSON.stringify([this.row, Math.min(this.col, COL - 1), focus]);
    } else {
      return null;
    }
  }

  word(char = '\u200b') {
    if (char == '\u200b') {
      return new Word(char, false, false, false, false, false, '', '');
    } else {
      return new Word(char, this.bright, this.underline, this.flash, this.inverse, this.invisable, this.color, this.background);
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
    escP: /\x1b\[\d{0,}P/,
    escm: /\x1b\[[\d;]{0,}m/
  };

  position(cursor) {
    return this[this.index].position(cursor);
  }

  input(utf8) {
    var COL = parseInt(this.width / WIDTH0);
    var line = this[this.index];
    for (var char of utf8) {
      var cursor = this.row * COL + this.col;
      var width = TerminalChild.measureChar(char) / WIDTH0;
      if (width == 1) {
        var p = this.position(cursor);
        if (p.eof != null) {
          for (var i = 0; i < p.eof; i++) {
            line.words.push(this.word());
          }
          line.words.push(this.word(char));
        } else {
          var w = TerminalChild.measureChar(line.words[p.index].value) / WIDTH0;
          if (p.offset >= 0) {
            if (w == 1) {
              line.words.splice(p.index, 1, this.word(char));
            } else {
              if (p.offset == 0) {
                line.words.splice(p.index, 1, this.word(char), this.word());
              } else {
                line.words.splice(p.index, 1, this.word(), this.word(char));
              }
            }
          } else {
            line.words.splice(p.index, 0, this.word(char));
          }
        }
      } else {
        var p = this.position(cursor);
        if (p.eof == null) {
          if (this.col == COL - 1) {
            cursor++;
            p = this.position(cursor);
          }
        }
        if (p.eof != null) {
          for (var i = 0; i < p.eof; i++) {
            line.words.push(this.word());
          }
          line.words.push(this.word(char));
        } else {
          var w = TerminalChild.measureChar(line.words[p.index].value) / WIDTH0;
          if (w == 1) {
            var p2 = this.position(cursor + 1);
            if (p2.eof != null || p2.offset < 0) {
              line.words.splice(p.index, 1, this.word(char));
            } else {
              var w2 = TerminalChild.measureChar(line.words[p2.index].value) / WIDTH0;
              if (w2 == 1) {
                line.words.splice(p.index, 2, this.word(char));
              } else {
                line.words.splice(p.index, 2, this.word(char), this.word());
              }
            }
          } else {
            if (p.offset == 0) {
              line.words.splice(p.index, 1, this.word(char));
            } else {
              var p2 = this.position(cursor + 1);
              if (p2.eof != null || p2.offset < 0) {
                line.words.splice(p.index, 1, this.word(), this.word(char));
              } else {
                var w2 = TerminalChild.measureChar(line.words[p2.index].value) / WIDTH0;
                if (w2 == 1) {
                  line.words.splice(p.index, 2, this.word(), this.word(char));
                } else {
                  line.words.splice(p.index, 2, this.word(), this.word(char), this.word());
                }
              }
            }
          }
        }
      }
      if (this.col + width <= COL) {
        this.col += width;
      } else {
        this.row++;
        this.col = width;
      }
      line.limit = Math.max(line.limit, this.row * COL + this.col);
    }
    line.invalidate();
  }

  lf() {
    var ROW = this[this.index].lineCount;
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
    var n = parseInt(utf8.substring(2, utf8.length - 1) || '1');
    for (var i = 0; i < n; i++) {
      if (this.row - 1 >= 0) {
        this.row--;
      }
    }
  }

  escB(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) || '1');
    var ROW = this[this.index].lineCount;
    for (var i = 0; i < n; i++) {
      if (this.row + 1 < ROW) {
        this.row++;
      }
    }
  }

  escC(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) || '1');
    var COL = parseInt(this.width / WIDTH0);
    for (var i = 0; i < n; i++) {
      if (this.col + 1 <= COL) {
        this.col++;
      }
    }
  }

  escD(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) || '1');
    for (var i = 0; i < n; i++) {
      if (this.col - 1 >= 0) {
        this.col--;
      }
    }
  }

  escK() {
    this.escP('\x1b[999P');
  }

  escP(utf8) {
    var n = parseInt(utf8.substring(2, utf8.length - 1) || '1');
    var COL = parseInt(this.width / WIDTH0);
    var cursor = this.row * COL + this.col;
    var col = this.col;
    if (COL - col <= 0) {
      return;
    }
    var line = this[this.index];
    var words = [];
    for (var c = cursor + n; c < (this.row + 1) * COL; c++) {
      var p = this.position(c);
      if (p.eof != null || p.offset < 0) {
        break;
      }
      if (p.offset == 0) {
        words.push(line.words[p.index]);
      } else {
        if (c == cursor + n) {
          words.push(this.word());
        }
      }
    }
    var width = 0;
    for (var word of words) {
      width += TerminalChild.measureChar(word.value) / WIDTH0;
    }
    for (var i = 0; i < COL - col; i++) {
      this.input('\u200b');
    }
    this.col = col;
    line.words.splice(this.position(cursor).index, width, ...words);
    line.invalidate();
  }

  escm(utf8) {
    for (var m of utf8.substring(2, utf8.length - 1).split(';')) {
      m = parseInt(m);
      if (m == 0) {
        this.bright = false;
        this.underline = false;
        this.flash = false;
        this.inverse = false;
        this.invisable = false;
        this.color = '';
        this.background = '';
      } else if (m == 1) {
        this.bright = true;
      } else if (m == 4) {
        this.underline = true;
      } else if (m == 5) {
        this.flash = true;
      } else if (m == 7) {
        this.inverse = true;
      } else if (m == 8) {
        this.invisable = true;
      } else if (m >= 30 && m <= 37) {
        this.color = COLORS[m - 30];
      } else if (m >= 40 && m <= 47) {
        this.background = COLORS[m - 40];
      }
    }
  }

  readu(utf8) {
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
    TerminalChild: TerminalChild,
    TerminalInput: TerminalInput
  },
  data: function() {
    return {
      lineHeight: HEIGHT0,
      source: null,
      inputLeft: 0,
      inputTop: 0
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
          this.source = new Source(this.$el.clientWidth - 24);
        }
        this.source.readu(oldValue == undefined ? newValue : newValue.substring(oldValue.length));
        this.updateCursor();
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
    isEmpty: function() {
      return this.source.length == 1 && this.source[0].value.length == 0;
    },
    copyLog: function() {
      var text = '';
      for (var i = 0; i < this.source.length; i++) {
        if (i != 0) {
          text += '\n';
        }
        text += this.source[i].value.replace(/\u200b/g, '');
      }
      this.$toast.alert('Text Copied');
      copyText(text);
    },
    onInput: function(utf8) {
      if (utf8) {
        asmdb.getInstance().writeu(utf8);
      }
      var parent = this.$refs.parent;
      if (!parent) {
        return;
      }
      parent.attachTo();
    },
    onScroll2: function() {
      this.updateCursor();
    },
    onResize: function() {
      this.updateCursor();
    },
    updateCursor: function() {
      var parent = this.$refs.parent;
      if (!parent) {
        return;
      }
      var cursor = this.source.getCursor(parent.getPosition());
      var h = 14;
      if (cursor[1] <= -h || cursor[1] >= this.$el.clientHeight) {
        this.inputLeft = 0;
        this.inputTop = this.$el.clientHeight - h;
      } else {
        this.inputLeft = cursor[0];
        this.inputTop = cursor[1];
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.terminal-container {
  position: relative;
  .terminal-parent {
    margin: 0px 12px;
    height: 100%;
  }
  .terminal-input {
    position: absolute;
    z-index: 4;
  }
}
</style>
