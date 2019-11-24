<template>
  <div class="world-container" :style="{width:screenWidth+'px'}">
    <div class="world-left-layout">
      <Bar ref="bar" class="world-bar"></Bar>
      <Assembly ref="assembly" class="world-assembly"></Assembly>
      <div class="world-points-layout">
        <Breakpoints ref="breakpoints" class="world-breakpoints" @clickitem="onClickItem"></Breakpoints>
        <div class="world-points-split"></div>
        <Watchpoints ref="watchpoints" class="world-watchpoints" @clickitem="onClickItem"></Watchpoints>
      </div>
      <Python3 ref="python3" class="world-python3"></Python3>
    </div>
    <div class="world-right-layout">
      <Registers ref="registers" class="world-registers" @clickitem="onClickItem"></Registers>
      <div class="world-heap-layout">
        <Stack ref="stack" class="world-stack" @clickitem="onClickItem"></Stack>
        <div class="world-heap-split"></div>
        <Memory ref="memory" class="world-memory" @clickitem="onClickItem"></Memory>
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
  computed: {
    screenWidth: function() {
      return screen.width;
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

.world-container {
  width: 100%;
  height: 100%;
  display: flex;

  .world-left-layout {
    flex-grow: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    .world-bar {
      background: @color-background-dark;
    }
    .world-assembly {
      flex-grow: 1;
      border-top: 1px solid @color-border;
      border-bottom: 1px solid @color-border;
      background: @color-background;
    }
    .world-points-layout {
      display: flex;
      .world-breakpoints {
        flex-grow: 1;
        background: @color-background;
      }
      .world-points-split {
        width: 1px;
        height: 100%;
        background: @color-border;
      }
      .world-watchpoints {
        background: @color-background;
      }
    }
  }

  .world-right-layout {
    z-index: 1;
    height: 100%;
    box-shadow: 0px 0px 6px @color-border-shadow;
    display: flex;
    flex-direction: column;
    .world-registers {
      background: @color-background;
    }
    .world-heap-layout {
      flex-grow: 1;
      display: flex;
      border-top: 1px solid @color-border;
      .world-stack {
        height: 100%;
        background: @color-background;
      }
      .world-heap-split {
        width: 1px;
        height: 100%;
        background: @color-border;
      }
      .world-memory {
        height: 100%;
        background: @color-background;
      }
    }
  }
}
</style>
