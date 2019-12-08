<template>
  <div class="world-container" :style="{width:screenWidth+'px'}">
    <div class="world-left-layout">
      <Bar ref="bar" class="world-bar"></Bar>
      <div class="world-code-layout">
        <Assembly ref="assembly" class="world-assembly"></Assembly>
        <Python3 ref="python3" class="world-python3"></Python3>
      </div>
      <div class="world-points-layout">
        <Breakpoints ref="breakpoints" class="world-breakpoints" @clickitem="onClickItem"></Breakpoints>
        <div class="world-points-split"></div>
        <Watchpoints ref="watchpoints" class="world-watchpoints" @clickitem="onClickItem"></Watchpoints>
      </div>
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
  computed: {
    screenWidth: function() {
      return screen.width;
    }
  },
  created: function() {
    asmdb.newInstance();
    asmdb.getInstance().registerEvent('world', this);
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('world', this);
    asmdb.oldInstance();
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
    },
    onQuit: function() {
      this.$inquiry.alert('Your process is offline, Do you want to quit now?', this.quit.bind(this));
    },
    quit: function() {
      this.$router.replace('/hello');
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
    .world-code-layout {
      position: relative;
      height: 0px;
      flex-grow: 1;
      border-top: 1px solid @color-background-dark;
      .world-assembly {
        height: 100%;
        background: @color-background;
      }
      .world-python3 {
        position: absolute !important;
        bottom: 0px;
        width: 100%;
      }
    }
    .world-points-layout {
      display: flex;
      .world-breakpoints {
        flex-grow: 1;
        background: @color-background-dark;
      }
      .world-points-split {
        width: 1px;
        align-self: stretch;
        background: @color-border;
      }
      .world-watchpoints {
        background: @color-background-dark;
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
      height: 0px;
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
