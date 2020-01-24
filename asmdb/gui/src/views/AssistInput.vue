<template>
  <div class="assist-input-container">
    <div :style="{backgroundImage:backgroundImage}"></div>
    <input ref="input" type="text" v-model="value" @focus="onFocus" @blur="onBlur" />
    <div class="assist-input-assist" v-show="opacity>0" :style="{opacity:opacity}">
      <div @mousedown="requestFocus">
        <div v-if="assist==null">loading</div>
        <div v-for="item in assist" :key="item" @click="onClickItem(item)">{{item}}</div>
      </div>
    </div>
  </div>
</template>

<script>
import Animation from '@/scripts/animation';

export default {
  data: function() {
    return {
      anim: new Animation(Animation.ease_out(224))
    };
  },
  props: {
    icon: String,
    value: String,
    assist: Array
  },
  computed: {
    backgroundImage: function() {
      var url = '/static/icons/' + this.icon + '.png';
      return "url('" + url + "')";
    },
    opacity: function() {
      return this.anim.value;
    }
  },
  methods: {
    onFocus: function() {
      this.anim.$target(1);
    },
    onBlur: function() {
      this.anim.$target(0);
    },
    requestFocus: function() {
      setTimeout(() => {
        this.$refs.input.focus();
      });
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
  > div:first-child {
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
  > input {
    width: 100%;
    padding-left: 36px;
    padding-right: 12px;
    line-height: 32px;
    font-size: 12px;
    color: @color-text;
    text-overflow: ellipsis;
  }
  .assist-input-assist {
    position: absolute;
    z-index: 1;
    width: 100%;
    padding-left: 24px;
    > div {
      width: 100%;
      overflow-y: scroll;
      background: @color-text;
      box-shadow: 0px 2px 6px @color-border-shadow;
      > div {
        padding-left: 12px;
        padding-right: 12px;
        font-size: 12px;
        line-height: 24px;
        color: @color-background-darker;
        cursor: pointer;
      }
      > div:hover {
        background: @color-text-dark;
      }
    }
  }
}
</style>
