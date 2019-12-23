<template>
  <div class="terminal-container">
    <TerminalParent class="terminal-parent" :source="source" #default="props">
      <TerminalChild :value="props.item.value" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></TerminalChild>
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
      value: 'Python 3.6.3 (default, Oct  4 2017, 06:09:05) ',
      height: 16
    };
    source[1] = {
      value: '[GCC 4.2.1 Compatible Apple LLVM 8.0.0 (clang-800.0.42.1)] on darwin',
      height: 16
    };
    source[2] = {
      value: 'Type "help", "copyright", "credits" or "license" for more information.',
      height: 16
    };
    source[3] = {
      value: '>>> ',
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
