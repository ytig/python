<template>
  <div class="assist-input-container">
    <div :style="{backgroundImage:backgroundImage}"></div>
    <div v-show="focus&&value.length>0" @mousedown="requestFocus" @click="onClose"></div>
    <input ref="input" type="text" :value="value" @input="onInput" @keydown="onKeyDown" @focus="onFocus" @blur="onBlur" spellcheck="false" />
    <div v-if="height>0" ref="assist" class="assist-input-assist" @mousedown="requestFocus" :style="{height:(height+2)+'px'}">
      <div class="assist-input-loading" v-if="assist==null">loading</div>
      <pre class="assist-input-item" v-for="(item, index) in assist" :key="item" @mouseenter="onMouseEnterItem(index)" @mousemove="onMouseMoveItem(index)" @mouseleave="onMouseLeaveItem(index)" @click="onClickItem(item)" :css-selected="index==selected">{{getSimpleItem(type,item)}}</pre>
    </div>
  </div>
</template>

<script>
import Animation from '@/scripts/animation';
const LINE_HEIGHT = 22;
const LINE_COUNT = 7.5;

export default {
  data: function() {
    return {
      focus: false,
      counter: 0,
      selected: -1,
      selecting: false,
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
    type: String,
    value: String,
    assist: Array
  },
  watch: {
    focus: function() {
      this.selected = -1;
      this.onAnim();
    },
    assist: function() {
      this.selected = -1;
      this.onAnim();
      var assist = this.$refs.assist;
      if (assist) {
        assist.scrollTop = 0;
      }
    }
  },
  computed: {
    backgroundImage: function() {
      var url = '/static/icons/' + this.icon + '.png';
      return "url('" + url + "')";
    },
    height: function() {
      return LINE_COUNT * LINE_HEIGHT * this.anim.value;
    }
  },
  created: function() {
    window.addEventListener('mousemove', this.onDomMouseMove, true);
  },
  destroyed: function() {
    window.removeEventListener('mousemove', this.onDomMouseMove, true);
  },
  methods: {
    getSimpleItem: function(type, item) {
      switch (type) {
        case 'file':
          var isdir = false;
          var count = 0;
          var simpleItem = null;
          for (var i of item.split('/').reverse()) {
            if (i) {
              count += 1;
              if (simpleItem == null) {
                simpleItem = './' + i + (isdir ? '/' : '');
              }
            }
            isdir = true;
          }
          return count <= 1 ? item : simpleItem;
        default:
          return item;
      }
    },
    selectEnd: function() {
      var input = this.$refs.input;
      input.selectionStart = input.selectionEnd = input.value.length;
      input.scrollLeft = input.scrollWidth - input.clientWidth;
    },
    onFocus: function() {
      this.counter++;
      this.focus = true;
    },
    onBlur: function() {
      var counter = ++this.counter;
      setTimeout(() => {
        if (counter != this.counter) {
          return;
        }
        this.focus = false;
      });
    },
    requestFocus: function() {
      setTimeout(() => {
        this.$refs.input.focus();
      });
    },
    onAnim: function() {
      if (this.focus) {
        var row = this.assist == null ? 1 : this.assist.length;
        var target = Math.min(row / LINE_COUNT, 1);
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
    onKeyDown: function(event) {
      if (event.keyCode == 13) {
        if (this.assist != null && this.assist.length > 0) {
          var selected = this.selected;
          if (!(selected >= 0 && selected < this.assist.length)) {
            selected = 0;
          }
          this.onClickItem(this.assist[selected]);
        }
      } else if (event.keyCode == 38 || event.keyCode == 40) {
        var down = event.keyCode == 40;
        if (this.assist != null && this.assist.length > 0) {
          var selected = this.selected;
          if (!(selected >= 0 && selected < this.assist.length)) {
            selected = down ? 0 : this.assist.length - 1;
          } else {
            selected += down ? 1 : -1;
          }
          this.selected = selected;
          this.selecting = true;
          if (selected >= 0 && selected < this.assist.length) {
            var assist = this.$refs.assist;
            if (assist) {
              var top = LINE_HEIGHT * selected;
              var bottom = top + LINE_HEIGHT;
              if (top < assist.scrollTop) {
                assist.scrollTop = top;
              }
              if (bottom > assist.scrollTop + LINE_COUNT * LINE_HEIGHT) {
                assist.scrollTop = bottom - LINE_COUNT * LINE_HEIGHT;
              }
            }
          }
        }
      } else {
        return;
      }
      event.preventDefault();
    },
    onMouseEnterItem: function(index) {
      if (!this.selecting) {
        this.selected = index;
      }
    },
    onMouseMoveItem: function(index) {
      if (!this.selecting) {
        this.selected = index;
      }
    },
    onMouseLeaveItem: function(index) {
      if (!this.selecting) {
        this.selected = -1;
      }
    },
    onClickItem: function(item) {
      this.$emit('input', item);
      this.$nextTick(this.selectEnd);
    },
    onDomMouseMove: function() {
      this.selecting = false;
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
  box-shadow: inset 0px 2px 7px fade(@color-border-shadow, 80%);
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
    color: @color-text;
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
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      cursor: pointer;
    }
    .assist-input-item[css-selected] {
      background: @color-background-hover;
    }
  }
}
</style>
