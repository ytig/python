<template>
  <div class="debug-container">
    <div class="debug-left-layout">
      <Bar ref="bar" class="debug-bar"></Bar>
      <Assembly ref="assembly" class="debug-assembly"></Assembly>
      <div class="debug-points-layout">
        <Breakpoints ref="breakpoints" class="debug-breakpoints" @clickitem="onClickItem"></Breakpoints>
        <div class="debug-points-split"></div>
        <Watchpoints ref="watchpoints" class="debug-watchpoints" @clickitem="onClickItem"></Watchpoints>
      </div>
      <Python3 ref="python3" class="debug-python3"></Python3>
    </div>
    <div class="debug-right-layout">
      <Registers ref="registers" class="debug-registers" @clickitem="onClickItem"></Registers>
      <div class="debug-heap-layout">
        <Stack ref="stack" class="debug-stack" @clickitem="onClickItem"></Stack>
        <div class="debug-heap-split"></div>
        <Memory ref="memory" class="debug-memory" @clickitem="onClickItem"></Memory>
      </div>
    </div>
  </div>
</template>

<script>
import asmdb from '@/scripts/asmdb';

export default {
  created: function() {
    if (!asmdb.getInstance()) {
      asmdb.newInstance(); //todo catch
    }
  },
  methods: {
    onClickItem: function(usage, address) {
      switch (usage) {
        case 0:
          this.$refs.assembly.jumpTo(address);
          break;
        case 1:
          if (!this.$refs.stack.jumpTo(address)) {
            this.$refs.memory.jumpTo(address);
          }
          break;
        case 2:
          this.$refs.memory.jumpTo(address);
          break;
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.debug-container {
  width: 100%;
  height: 100%;
  display: flex;

  .debug-left-layout {
    flex-grow: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    .debug-bar {
      background: @color-background-dark;
    }
    .debug-assembly {
      flex-grow: 1;
      border-top: 1px solid @color-border;
      border-bottom: 1px solid @color-border;
      background: @color-background;
    }
    .debug-points-layout {
      display: flex;
      .debug-breakpoints {
        flex-grow: 1;
        background: @color-background;
      }
      .debug-points-split {
        width: 1px;
        height: 100%;
        background: @color-border;
      }
      .debug-watchpoints {
        background: @color-background;
      }
    }
  }

  .debug-right-layout {
    z-index: 1;
    height: 100%;
    box-shadow: 0px 0px 6px @color-border-shadow;
    display: flex;
    flex-direction: column;
    .debug-registers {
      background: @color-background;
    }
    .debug-heap-layout {
      flex-grow: 1;
      display: flex;
      border-top: 1px solid @color-border;
      .debug-stack {
        height: 100%;
        background: @color-background;
      }
      .debug-heap-split {
        width: 1px;
        height: 100%;
        background: @color-border;
      }
      .debug-memory {
        height: 100%;
        background: @color-background;
      }
    }
  }
}
</style>
