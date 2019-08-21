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
    <Indicator :size="10" :value="page" @input="page=arguments[0];invalidate()" :disable="disable2"></Indicator>
  </div>
</template>

<script>
import asmdb from "@/scripts/asmdb.js";

class Logic {
  constructor() {
    this.sp = null;
    this.oldData = null;
    this.newData = null;
    this.pageCache = {};
  }

  onBreak(sp, stack) {
    console.log("onBreak");
    //todo
    // if (this._sp != sp) {
    //     this._pageCache[this._sp] = this.page;
    //     this._sp = sp;
    //     this.page = this._sp in this._pageCache ? this._pageCache[this._sp] : 0;
    //     this._oldData = null;
    //     this._newData = stack;
    //   } else {
    //     this._oldData = this._newData;
    //     this._newData = stack;
    //   }
  }

  onContinue() {}

  getItems(page, pageSize) {
    console.log("getItems");
    return [];
  }
}

export default {
  data: function() {
    return {
      disable: true,
      disable2: true,
      items: [],
      page: 0,
      logic: new Logic()
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
      this.logic.onBreak(sp, stack);
      this.invalidate();
    },
    onContinue: function() {
      this.disable = true;
      this.logic.onContinue();
    },
    invalidate: function() {
      var ref = this.$refs.stackLayout;
      var pageSize = ref ? Math.floor(ref.clientHeight / 14) : 0;
      this.items.splice(0, this.items.length, ...this.logic.getItems(this.page, pageSize));
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
