<template>
  <div class="assembly-container">
    <Navigation :name="'Assembly'" :focus="focus" :disable="disable" :gradient="true"></Navigation>
    <div class="assembly-column">
      <div class="assembly-row">
        <Scroller ref="scroller" class="assembly-scroller" :source="source" #default="props">
          <Instruction :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></Instruction>
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
        source[i] = {
          height: 18,
          lineNumber:
            (i >= 0 ? '+' : '-') +
            '0x' +
            Math.abs(i)
              .toString(16)
              .zfill(3),
          value: {
            newBytes: '0000000000000000',
            oldBytes: ''
          }
        };
      }
      source.invalidate++;
    }, 1000);
    return {
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
