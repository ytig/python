<template>
  <div v-show="show" class="inquiry-container">
    <div class="inquiry-grow"></div>
    <div class="inquiry-content">
      <div class="inquiry-message">{{message}}</div>
      <div class="inquiry-button2">
        <span class="inquiry-button user-select-none" @click="onClickItem(0, ...arguments)">Yes</span>
        <div class="inquiry-split"></div>
        <span class="inquiry-button user-select-none" @click="onClickItem(1, ...arguments)">No</span>
      </div>
    </div>
    <div class="inquiry-grow"></div>
  </div>
</template>

<script>
export default {
  data: function() {
    return {
      show: false,
      message: '',
      listener: null
    };
  },
  methods: {
    alert: function(message, listener) {
      this.show = true;
      this.message = message;
      this.listener = listener || null;
    },
    close: function() {
      this.show = false;
      this.message = '';
      this.listener = null;
    },
    onKeyDown: function(event) {
      return this.show;
    },
    onClickItem: function(index, event) {
      if (index == 0) {
        if (this.listener != null) {
          this.listener();
        }
      }
      this.listener = null;
      this.close();
      event.stopPropagation();
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.inquiry-container {
  position: fixed;
  z-index: 7;
  left: 0px;
  top: 0px;
  width: 100%;
  height: 100%;
  background: #00000080;
  display: flex;
  flex-direction: column;
  align-items: center;
  .inquiry-grow {
    flex-grow: 1;
  }
  .inquiry-content {
    min-width: 201px;
    max-width: 401px;
    background: @color-background-dark;
    box-shadow: 6px 12px 12px @color-border-shadow;
    .inquiry-message {
      padding-left: 12px;
      padding-top: 16px;
      padding-right: 20px;
      padding-bottom: 12px;
      line-height: 18px;
      font-size: 12px;
      color: @color-text-menu;
    }
    .inquiry-button2 {
      border-top: 1px solid @color-border-light;
      display: flex;
      .inquiry-button {
        width: 0px;
        flex-grow: 1;
        line-height: 32px;
        text-align: center;
        font-size: 12px;
        color: @color-text-menu;
        cursor: pointer;
      }
      .inquiry-button:hover {
        background: @color-background-hover;
      }
      .inquiry-split {
        width: 1px;
        align-self: stretch;
        background: @color-border-light;
      }
    }
  }
}
</style>
