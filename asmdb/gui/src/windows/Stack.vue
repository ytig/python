<template>
  <div class="stack-container">
    <Navigation :name="'Stack'" :disable="disable"></Navigation>
    <div ref="stackLayout" class="stack-layout">
      <Empty v-if="items.length==0" :text="'[no data]'" style="padding-top:12px;"></Empty>
      <div v-else>
        <div v-for="item in items" :key="item.id">
          <div class="todo">+0x190 &nbsp;00 01 02 03 04 05 06 07</div>
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
  created: function() {
    asmdb.registerEvent("stack", this);
  },
  destroyed: function() {
    asmdb.unregisterEvent(this);
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
      this.logic.onContinue(this);
    },
    onClickIndex: function(newPage) {
      this.page = newPage;
      this.invalidate();
    },
    invalidate: function() {
      var ref = this.$refs.stackLayout;
      var page = this.page;
      var pageSize = ref ? Math.floor(ref.clientHeight / 14) : 0;
      var items = [];
      //todo
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
    width: 248px; //todo
    padding: 0px 12px;
  }
}
</style>
