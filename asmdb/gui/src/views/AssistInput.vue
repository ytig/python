<template>
  <div class="assist-input-container">
    <div :style="{backgroundImage:backgroundImage}"></div>
    <div v-show="focus.bool_f&&value.length>0" @mousedown="requestFocus" @click="onClose"></div>
    <input ref="input" type="text" :value="value" @input="onInput" @focus="onFocus" @blur="onBlur" />
    <div v-show="height>0" class="assist-input-assist" @mousedown="requestFocus" :style="{height:(height+2)+'px'}">
      <div class="assist-input-loading" v-if="assist==null">loading</div>
      <div class="assist-input-item" v-for="item in assist" :key="item" @click="onClickItem(item)">{{item}}</div>
    </div>
  </div>
</template>

<script>
import Animation from '@/scripts/animation';
import sloth from '@/scripts/sloth';

//文本过长显示问题
//loading优化

export default {
  data: function() {
    return {
      focus: new sloth(0),
      anim: new Animation((value, target) => {
        const power = 0.75;
        const duration = 180;
        var speed = (Math.pow(Math.abs(target - value), power) * Math.pow(0.1, 1 - power)) / ((1 - power) * duration);
        return Math.max(speed, 1 / 3000);
      })
    };
  },
  props: {
    icon: String,
    value: String,
    assist: Array
  },
  watch: {
    assist: function() {
      this.onAnim();
    }
  },
  computed: {
    backgroundImage: function() {
      var url = '/static/icons/' + this.icon + '.png';
      return "url('" + url + "')";
    },
    height: function() {
      return 7.5 * 22 * this.anim.value;
    }
  },
  methods: {
    onFocus: function() {
      this.focus.set(true);
      this.onAnim();
    },
    onBlur: function() {
      this.focus.set(false);
      this.onAnim();
    },
    requestFocus: function() {
      setTimeout(() => {
        this.$refs.input.focus();
      });
    },
    onAnim: function() {
      if (this.focus.bool_t) {
        var row = this.assist == null ? 1 : this.assist.length;
        var target = Math.min(row / 7.5, 1);
        this.anim.$target(target);
      } else {
        this.anim.$target(0);
      }
    },
    onClose: function() {
      this.$emit('input', '');
    },
    onInput: function() {
      this.$emit('input', this.$refs.input.value);
    },
    onClickItem: function(item) {
      this.$emit('input', item);
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.assist-input-container {
  position: relative;
  height: 32px;
  border-radius: 4px;
  background-color: @color-background-darker;
  box-shadow: inset 0px 2px 8px rgba(0, 0, 0, 0.8);
  > div:nth-child(1) {
    position: absolute;
    left: 12px;
    top: 8px;
    width: 16px;
    height: 16px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    pointer-events: none;
  }
  > div:nth-child(2) {
    position: absolute;
    right: -28px;
    top: 4px;
    width: 24px;
    height: 24px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    background-image: url('/static/icons/close.png');
    cursor: pointer;
  }
  > input {
    width: 100%;
    padding-left: 36px;
    padding-right: 12px;
    line-height: 32px;
    font-size: 12px;
    color: @color-text-menu;
    text-overflow: ellipsis;
  }
  .assist-input-assist {
    position: absolute;
    z-index: 1;
    width: 100%;
    left: 0px;
    top: 36px;
    background: @color-background-dark;
    border: 1px solid @color-border-light;
    box-shadow: 0px 4px 6px @color-border-shadow;
    overflow-y: scroll;
    .assist-input-loading {
      text-align: center;
      font-size: 12px;
      line-height: 22px;
      color: @color-text-menu-dark;
    }
    .assist-input-item {
      padding-left: 36px;
      padding-right: 12px;
      font-size: 12px;
      line-height: 22px;
      color: @color-text-menu;
      cursor: pointer;
    }
    .assist-input-item:hover {
      background: @color-background-hover;
    }
  }
}
</style>
