<template>
  <div class="terminal-container">
    <TerminalParent v-if="source!=null" class="terminal-parent" :source="source" #default="props">
      <TerminalChild :value="props.item.value" :styles="props.item.styles" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></TerminalChild>
    </TerminalParent>
  </div>
</template>

<script>
import resize from '@/scripts/resize';
import asmdb from '@/scripts/asmdb';
import TerminalParent from './Terminal_parent';
import TerminalChild from './Terminal_child';
//foucs
//width height -> setwinsize
//linux bytes
//input -> writeb 粘贴，中文输入：悬浮
//scroll infinite
class Source {
  constructor() {
    this.width = 0;
    this.height = 0;
    this.length = 0;
    this.cursor = 0;
    this.background = '';
    this.color = '';
    this.invalidate = 0;
    this.readu('\r\n');
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
  }

  readu(utf8) {
    for (var item of this.splitu(utf8, /\r\n/, /\x02/)) {
      var type = item[0];
      var value = item[1];
      switch (type) {
        case 0:
          var newValue = this[this.length - 1].value.substring(0, this.cursor) + value + this[this.length - 1].value.substring(this.cursor + value.length);
          this[this.length - 1].value = newValue;
          var newStyles = JSON.parse(this[this.length - 1].styles);
          newStyles = [[newValue.length, '', '']]; //todo
          this[this.length - 1].styles = JSON.stringify(newStyles);
          this[this.length - 1].height = TerminalChild.measureHeight(this.width, newValue);
          this.cursor += value.length;
          break;
        case 1:
          this[this.length++] = {
            value: '',
            styles: '[]',
            height: TerminalChild.measureHeight(this.width, '')
          };
          this.cursor = 0;
          break;
        case 2:
          switch (value) {
            case '\x02':
              this.cursor--;
              break;
          }
          break;
      }
    }
    this.invalidate++;
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
    foucs: Boolean,
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
