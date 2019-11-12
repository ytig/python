<template>
  <div class="assembly-container">
    <Navigation :name="'Assembly'"></Navigation>
    <Scroller ref="scroller" class="assembly-scroller" :source="source" #default="props">
      <Bytes :startAddress="0" :lineNumber="props.item.lineNumber" :value="props.item.value" :group="8" :canvasContext="props.offset+';'+props.context" :lazyLayout="props.scrolling"></Bytes>
    </Scroller>
  </div>
</template>

<script>
export default {
  data: function() {
    var source = {}; //for test
    for (var i = -99; i < 100; i++) {
      source[i] = {
        height: 18,
        lineNumber: '' + i,
        value: {
          newBytes: '123',
          oldBytes: ''
        }
      };
    }
    return {
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
  .assembly-scroller {
    width: 147px;
    height: 0px;
    flex-grow: 1;
  }
}
</style>
