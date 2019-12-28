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
    if (!utf8) {
      return;
    }
    if (utf8.indexOf('\r\n') >= 0) {
      var i = 0;
      for (var line of utf8.split('\r\n')) {
        if (i++ != 0) {
          this[this.length++] = {
            value: '',
            styles: '[]',
            height: TerminalChild.measureHeight(this.width, '')
          };
          this.cursor = 0;
          this.invalidate++;
        }
        this.readu(line);
      }
      return;
    }
    var newValue = this[this.length - 1].value.substring(0, this.cursor) + utf8 + this[this.length - 1].value.substring(this.cursor);
    this[this.length - 1].value = newValue;
    this[this.length - 1].styles = JSON.stringify([[newValue.length, '', '']]); //todo
    this[this.length - 1].height = TerminalChild.measureHeight(this.width, newValue);
    this.cursor += utf8.length;
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
