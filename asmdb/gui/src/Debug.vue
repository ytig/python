<template>
  <div id="root">
    <div id="left-layout">
      <Bar id="bar"></Bar>
      <Assembly id="assembly" ref="assembly"></Assembly>
      <div id="points-layout">
        <Breakpoints id="breakpoints"></Breakpoints>
        <div id="points-split"></div>
        <Watchpoints id="watchpoints"></Watchpoints>
      </div>
      <Python3 id="python3"></Python3>
    </div>
    <div id="right-layout">
      <Registers id="registers" @clickitem="onClickItem"></Registers>
      <div id="heap-layout" ref="heapLayout">
        <Stack id="stack" ref="stack" @clickitem="onClickItem"></Stack>
        <div id="heap-split"></div>
        <Memory id="memory" ref="memory" @clickitem="onClickItem"></Memory>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  methods: {
    onClickItem: function(usage, address) {
      switch (usage) {
        case 0:
          this.$refs.assembly.jumpTo(address);
          break;
        case 1:
          this.$refs.stack.jumpTo(1 + (address % 2560)); //for test
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

#root {
  width: 100%;
  height: 100%;
  display: flex;

  #left-layout {
    flex-grow: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    #bar {
      background: linear-gradient(@color-border, @color-background-dark 38.2%);
    }
    #assembly {
      flex-grow: 1;
      border-top: 1px solid @color-border;
      border-bottom: 1px solid @color-border;
      background: @color-background;
    }
    #points-layout {
      display: flex;
      #breakpoints {
        flex-grow: 1;
        height: 100%;
        background: @color-background;
      }
      #points-split {
        width: 1px;
        height: 100%;
        background: @color-border;
      }
      #watchpoints {
        background: @color-background;
      }
    }
  }

  #right-layout {
    height: 100%;
    box-shadow: 0px 0px 6px @color-border-shadow;
    display: flex;
    flex-direction: column;
    #registers {
      background: @color-background;
    }
    #heap-layout {
      flex-grow: 1;
      display: flex;
      border-top: 1px solid @color-border;
      #stack {
        height: 100%;
        background: @color-background;
      }
      #heap-split {
        width: 1px;
        height: 100%;
        background: @color-border;
      }
      #memory {
        height: 100%;
        background: @color-background;
      }
    }
  }
}
</style>
