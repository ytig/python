<template>
  <div class="terminal-container">
    <TerminalParent class="terminal-parent" :source="source" #default="props">
      <TerminalChild :value="props.item.value" :styles="props.item.styles" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></TerminalChild>
    </TerminalParent>
  </div>
</template>

<script>
import resize from '@/scripts/resize';
import TerminalParent from './Terminal_parent';
import TerminalChild from './Terminal_child';
//foucs
//width height -> setwinsize
//linux bytes
//input -> writeb 粘贴，中文输入：悬浮
//scroll infinite
export default {
  components: {
    TerminalParent: TerminalParent,
    TerminalChild: TerminalChild
  },
  data: function() {
    var source = {};
    source[0] = {
      value: '1234',
      styles: JSON.stringify([[2, 'red', ''], [2, '', '']]),
      height: 16
    };
    return {
      source: source
    };
  },
  mounted: function() {
    resize.registerEvent(this);
  },
  destroyed: function() {
    resize.unregisterEvent(this);
  },
  methods: {
    onResize: function() {}
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.terminal-container {
  .terminal-parent {
    height: 100%;
  }
}
</style>
