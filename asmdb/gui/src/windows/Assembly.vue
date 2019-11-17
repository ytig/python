<template>
  <div class="assembly-container">
    <Navigation :name="'Assembly'" :focus="focus" :disable="disable" :gradient="true"></Navigation>
    <div class="assembly-column">
      <div class="assembly-row">
        <Scroller ref="scroller" class="assembly-scroller" :source="source" #default="props">
          <Instruction :address="props.item.address" :mnemonic="props.item.mnemonic" :op_str="props.item.op_str" :highlight="props.item.highlight" :breaking="props.item.breaking" :group="instructionGroup" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></Instruction>
        </Scroller>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data: function() {
    var source = { invalidate: 0 }; //for test
    setTimeout(() => {
      for (var i = -99; i < 100; i++) {
        var j = 10000 + i;
        var addr = '0x' + j.toString(16).zfill(8);
        var mock = {
          height: 20,
          address: addr,
          mnemonic: 'ldr',
          op_str: 'r0 r1',
          highlight: false,
          breaking: 0
        };
        if (i == 0) {
          mock.highlight = true;
        }
        switch (j % 2) {
          case 1:
            mock.mnemonic = 'push';
            mock.op_str = 'pc, [r0 + 0x1234]';
            break;
        }
        source[i] = mock;
      }
      source.invalidate++;
    }, 1000);
    return {
      instructionGroup: 6,
      focus: false,
      disable: true,
      source: source
    };
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.assembly-container {
  position: relative;
  display: flex;
  flex-direction: column;
  .assembly-column {
    height: 0px;
    flex-grow: 1;
    display: flex;
    .assembly-row {
      width: 0px;
      flex-grow: 1;
      overflow-x: scroll;
      .assembly-scroller {
        width: 500px;
        height: 100%;
      }
    }
  }
}
</style>
