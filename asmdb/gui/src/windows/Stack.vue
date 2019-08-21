<template>
  <div class="stack-container">
    <Navigation :name="'Stack'" :disable="disable"></Navigation>
    <div class="stack-layout">
      <Empty v-if="itemsAtPage.length==0" :text="'[no data]'" style="padding-top:12px;"></Empty>
      <div v-else>
        <div v-for="item in itemsAtPage" :key="item.id">
          <div class="todo">+0x190 &nbsp;00 01 02 03 04 05 06 07</div>
        </div>
      </div>
    </div>
    <Indicator :size="10" v-model="page" :disable="sp==null"></Indicator>
  </div>
</template>

<script>
import asmdb from "@/scripts/asmdb.js";

export default {
  data: function() {
    return {
      disable: true,
      sp: null,
      oldData: null,
      newData: null,
      page: 0,
      pageCache: {}
    };
  },
  computed: {
    itemsAtPage: function() {
      //todo
      return [];
    }
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
      if (this.sp != sp) {
        this.pageCache[this.sp] = this.page;
        this.sp = sp;
        this.page = this.sp in this.pageCache ? this.pageCache[this.sp] : 0;
        this.oldData = null;
        this.newData = stack;
      } else {
        this.oldData = this.newData;
        this.newData = stack;
      }
    },
    onContinue: function() {
      this.disable = true;
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
