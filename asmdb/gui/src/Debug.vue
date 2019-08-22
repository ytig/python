<template>
  <div id="root">
    <div id="left-layout">
      <Bar id="bar"></Bar>
      <Assembly id="assembly"></Assembly>
      <div id="points-layout">
        <Breakpoints id="breakpoints"></Breakpoints>
        <Watchpoints id="watchpoints"></Watchpoints>
      </div>
      <Python3 id="python3"></Python3>
    </div>
    <div id="right-layout">
      <Registers id="registers"></Registers>
      <div id="heap-layout" ref="heapLayout">
        <Stack id="stack"></Stack>
        <Memory id="memory"></Memory>
      </div>
    </div>
  </div>
</template>

<script>
export default {};
</script>

<style lang="less">
@import '~@/styles/theme.less';

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
      background: @color-dark-background;
      border-bottom: 1px solid @color-border;
    }
    #assembly {
      flex-grow: 1;
    }
    #points-layout {
      background: @color-dark-background;
      border-top: 1px solid @color-border;
      border-bottom: 1px solid @color-border;
      display: flex;
      #breakpoints {
        flex-grow: 1;
        height: 100%;
        border-right: 1px solid @color-border;
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
        border-right: 1px solid @color-border;
      }
      #memory {
        height: 100%;
      }
    }
  }
}
</style>
