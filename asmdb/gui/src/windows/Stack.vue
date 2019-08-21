<template>
  <div class="stack-container">
    <Navigation :name="'Stack'" :disable="disable"></Navigation>
    <div ref="stackLayout" class="stack-layout">
      <Empty v-if="items.length==0" :text="'[no data]'" style="padding-top:12px;"></Empty>
      <div v-else>
        <div v-for="(item, index) in items" :key="index" class="stack-row">
          <div>{{item.addr}}</div>
          <div v-for="(_item, _index) in item.hexs" :key="_index" :class="_item.changed?'stack-changed':''">{{(_index%8==0?'&nbsp;':'')+'&nbsp;'+_item.hex}}</div>
        </div>
      </div>
    </div>
    <Indicator :size="10" :value="page" @input="onClickIndex" :disable="disable2"></Indicator>
  </div>
</template>

<script>
import asmdb from "@/scripts/asmdb.js";

export default {
  data: function() {
    return {
      disable: true,
      disable2: true,
      items: [],
      page: 0,
      dict: {
        sp: null,
        oldData: null,
        newData: null,
        pageCache: {}
      }
    };
  },
  props: {
    column: {
      type: Number,
      default: 1
    }
  },
  created: function() {
    asmdb.registerEvent("stack", this);
  },
  destroyed: function() {
    asmdb.unregisterEvent("stack", this);
  },
  methods: {
    onBreak: function(sp, stack) {
      this.disable = false;
      this.disable2 = false;
      var dict = this.dict;
      if (dict.sp != sp) {
        if (dict.sp != null) {
          dict.pageCache[dict.sp] = this.page;
        }
        dict.sp = sp;
        this.page = dict.sp in dict.pageCache ? dict.pageCache[dict.sp] : 0;
        dict.oldData = null;
        dict.newData = stack;
      } else {
        dict.oldData = dict.newData;
        dict.newData = stack;
      }
      this.invalidate();
    },
    onContinue: function() {
      this.disable = true;
    },
    onClickIndex: function(newPage) {
      this.page = newPage;
      this.invalidate();
    },
    invalidate: function() {
      var page = this.page;
      var column = this.column * 8;
      var row = this.$refs.stackLayout ? Math.floor(this.$refs.stackLayout.clientHeight / 14) : 0;
      var items = [];
      var start = page * column * row;
      var end = start + column * row;
      var oldData = this.dict.oldData != null ? this.dict.oldData.slice(2 * start, 2 * end) : "";
      var newData = this.dict.newData != null ? this.dict.newData.slice(2 * start, 2 * end) : "";
      for (var i = 0; i < row; i++) {
        var item = { addr: "+0x230", hexs: [] };
        for (var j = 0; j < column; j++) {
          var k = i * column + j;
          var new_data = newData.slice(2 * k, 2 * (k + 1));
          if (!new_data) {
            item = null;
            break;
          }
          var old_data = oldData.slice(2 * k, 2 * (k + 1));
          item.hexs[j] = {
            hex: new_data,
            changed: Boolean(old_data && new_data != old_data)
          };
        }
        if (item == null) {
          break;
        }
        if (item.hexs.length > 0) {
          items[i] = item;
        }
      }
      this.items.splice(0, this.items.length, ...items);
    }
  }
};
</script>

<style lang="less">
@import "~@/styles/theme.less";

.stack-container {
  display: flex;
  flex-direction: column;
  .stack-layout {
    flex-grow: 1;
    height: 0px;
    overflow-y: scroll;
    width: 248px; //todo
    .stack-row {
      display: flex;
      > *:first-child {
        padding-left: 12px;
        color: @color-darker-text;
      }
      > *:last-child {
        padding-right: 12px;
      }
      > * {
        color: @color-text;
        font-size: 12px;
      }
      > .stack-changed {
        color: @color-diff-text;
      }
    }
  }
}
</style>
