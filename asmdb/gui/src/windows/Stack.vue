<template>
  <div class="stack-container">
    <Navigation :name="'Stack'" :disable="disable"></Navigation>
    <div class="stack-layout">
      <div v-if="itemsAtPage.length==0" class="stack-empty user-select-none">[no data]</div>
      <div v-else>
        <div v-for="item in itemsAtPage" :key="item.id">
          <div class="todo">+0x190 &nbsp;00 01 02 03 04 05 06 07</div>
        </div>
      </div>
    </div>
    <Indicator :size="10" v-model="page" :disable="items.length==0"></Indicator>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      disable: true,
      items: [],
      page: 0
    };
  },
  computed: {
    itemsAtPage: function() {
      //todo splice items
      return this.items;
    }
  },
  created: function() {
    //todo listen regs
  },
  methods: {
    onItemsChange: function(items) {
      if (items == null) {
        this.disable = true;
      } else {
        this.disable = false;
        //todo changed info
        this.items.splice(0, this.items.length, ...items);
      }
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
    .stack-empty {
      text-align: center;
      color: @color-dark-content;
      font-size: 12px;
    }
  }
}
</style>
