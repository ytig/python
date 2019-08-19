<template>
  <div id="container">
    <div id="left_layout">
      <i-bar id="bar"></i-bar>
      <i-assembly id="assembly"></i-assembly>
      <div id="points_layout">
        <i-breakpoints id="breakpoints"></i-breakpoints>
        <i-watchpoints id="watchpoints"></i-watchpoints>
      </div>
      <i-python3 id="python3"></i-python3>
    </div>
    <div id="right_layout">
      <i-registers id="registers"></i-registers>
      <div id="heap_layout">
        <i-stack id="stack"></i-stack>
        <i-memory id="memory"></i-memory>
      </div>
    </div>
  </div>
</template>

<script>
import iAssembly from "@/windows/Assembly";
import iBar from "@/windows/Bar";
import iBreakpoints from "@/windows/Breakpoints";
import iMemory from "@/windows/Memory";
import iPython3 from "@/windows/Python3";
import iRegisters from "@/windows/Registers";
import iStack from "@/windows/Stack";
import iWatchpoints from "@/windows/Watchpoints";

export default {
  name: "Debug",
  components: {
    "i-assembly": iAssembly,
    "i-bar": iBar,
    "i-breakpoints": iBreakpoints,
    "i-memory": iMemory,
    "i-python3": iPython3,
    "i-registers": iRegisters,
    "i-stack": iStack,
    "i-watchpoints": iWatchpoints
  }
};
</script>

<style lang="less">
@import "~@/styles/global.less";

#container {
  position: fixed;
  width: 100%;
  height: 100%;
  display: flex;
  background: @color-background;

  #left_layout {
    flex-grow: 1;
    height: 100%;
    padding-bottom: 50px;
    display: flex;
    flex-direction: column;
    #bar {
      height: 40px;
      background: @color-dark-background;
      border-bottom: 1px solid @color-line;
    }
    #assembly {
      flex-grow: 1;
    }
    #points_layout {
      height: 160px;
      background: @color-dark-background;
      border-top: 1px solid @color-line;
      border-bottom: 1px solid @color-line;
    }
  }

  #right_layout {
    width: 890px;
    height: 100%;
    box-shadow: 0 5px 5px @color-shadow;
    #registers {
      height: 114px;
      border-bottom: 1px solid @color-line;
    }
  }
}
</style>
