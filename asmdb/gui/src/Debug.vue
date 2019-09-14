<template>
  <div id="root">
    <div id="left-layout">
      <Bar id="bar"></Bar>
      <Assembly id="assembly"></Assembly>
      <div id="points-layout">
        <Breakpoints id="breakpoints"></Breakpoints>
        <div id="points-split"></div>
        <Watchpoints id="watchpoints"></Watchpoints>
      </div>
      <Python3 id="python3"></Python3>
    </div>
    <div id="right-layout">
      <Registers id="registers"></Registers>
      <div id="heap-layout" ref="heapLayout">
        <Stack id="stack"></Stack>
        <div id="heap-split"></div>
        <Memory id="memory"></Memory>
      </div>
    </div>
  </div>
</template>

<script>
export default {};
</script>

<style lang="less">
@import '~@/styles/theme';

#root {
  width: 100%;
  height: 100%;
  display: flex;
  background: @color-background;

  #left-layout {
    flex-grow: 1;
    height: 100%;
    display: flex;
    flex-direction: column;
    #bar {
      background: @color-background-dark;
    }
    #assembly {
      flex-grow: 1;
      border-top: 1px solid @color-border;
      border-bottom: 1px solid @color-border;
    }
    #points-layout {
      background: @color-background-dark;
      display: flex;
      #breakpoints {
        flex-grow: 1;
        height: 100%;
      }
      #points-split {
        width: 1px;
        height: 100%;
        background: @color-border;
      }
    }
  }

  #right-layout {
    height: 100%;
    box-shadow: 0px 0px 6px @color-border-shadow;
    display: flex;
    flex-direction: column;
    #heap-layout {
      flex-grow: 1;
      display: flex;
      border-top: 1px solid @color-border;
      #stack {
        height: 100%;
      }
      #heap-split {
        width: 1px;
        height: 100%;
        background: @color-border;
      }
      #memory {
        height: 100%;
      }
    }
  }
}
</style>
