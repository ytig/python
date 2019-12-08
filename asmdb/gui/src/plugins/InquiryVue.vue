<template>
  <div v-show="anim.value!=0" class="inquiry-container" :style="{background:background}">
    <div class="inquiry-grow"></div>
    <div class="inquiry-content" :style="{opacity:opacity,transform:transform}">
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
import Animation from '@/scripts/animation';

export default {
  data: function() {
    return {
      message: '',
      listener: null,
      anim: new Animation(Animation.ease_out(224))
    };
  },
  computed: {
    background: function() {
      return 'rgba(0, 0, 0, ' + this.anim.value * 0.5 + ')';
    },
    opacity: function() {
      return this.anim.value;
    },
    transform: function() {
      return 'translateY(' + (1 - this.anim.value) * 50 + '%)';
    }
  },
  methods: {
    alert: function(message, listener) {
      this.anim.$target(1);
      this.message = message;
      this.listener = listener || null;
    },
    close: function() {
      this.anim.$target(0);
      this.listener = null;
    },
    onKeyDown: function(event) {
      var show = this.anim.value != this.anim.target || this.anim.value != 0;
      return show;
    },
    onClickItem: function(index, event) {
      if (index == 0) {
        if (this.listener != null) {
          this.listener();
        }
      }
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
