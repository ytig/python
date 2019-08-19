<template>
  <div id="container">
    <div id="left-layout">
      <i-bar id="bar"></i-bar>
      <i-assembly id="assembly"></i-assembly>
      <div id="points-layout">
        <i-breakpoints id="breakpoints"></i-breakpoints>
        <i-watchpoints id="watchpoints"></i-watchpoints>
      </div>
      <i-python3 id="python3"></i-python3>
    </div>
    <div id="right-layout">
      <i-registers id="registers"></i-registers>
      <div id="heap-layout">
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

  #left-layout {
    flex-grow: 1;
    height: 100%;
    padding-bottom: 50px;
    display: flex;
    flex-direction: column;
    #bar {
      height: 40px;
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
      #watchpoints {
        height: 160px;
      }
    }
  }

  #right-layout {
    width: 890px;
    height: 100%;
    box-shadow: 0 5px 5px @color-shadow;
    display: flex;
    flex-direction: column;
    #registers {
      border-bottom: 1px solid @color-border;
    }
    #heap-layout {
      flex-grow: 1;
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
