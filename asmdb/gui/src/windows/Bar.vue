<template>
  <div class="bar-container" @mouseup="onMouseUp">
    <div class="bar-icon"></div>
    <span class="bar-text">{{title}}</span>
    <div class="bar-item" v-for="(item, index) in items" :key="index" :title="item.title" :style="item.style" @click="onClickItem(index)" :css-enable="enable.enable_f"></div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';

class Enable {
  constructor(delay) {
    this.enable_t = false;
    this.enable_f = false;
    this.delay = delay;
    this.counter = 0;
  }

  onEnable(enable) {
    if (this.enable_t == enable) {
      return;
    }
    this.enable_t = enable;
    this.counter++;
    if (this.enable_t) {
      this.enable_f = true;
    } else {
      var counter = this.counter;
      setTimeout(() => {
        if (counter != this.counter) {
          return;
        }
        this.enable_f = false;
      }, this.delay);
    }
  }
}

export default {
  data: function() {
    return {
      enable: new Enable(224),
      title: 'com.example.app'
    };
  },
  computed: {
    items: function() {
      var titles = ['nexti', 'stepi', 'continue', 'release'];
      var icons = ['next', 'step', 'cont', 'rlse'];
      var items = [];
      for (var i = 0; i < 4; i++) {
        var title = titles[i];
        var image = "url('/static/icons/" + icons[i] + ".png'";
        if (this.enable.enable_f) {
          items.push({
            title: title,
            style: { backgroundImage: image }
          });
        } else {
          items.push({
            title: '',
            style: { maskImage: image }
          });
        }
      }
      return items;
    }
  },
  mounted: function() {
    keyboard.setDefaultWindow(this);
    asmdb.getInstance().registerEvent('bar', this);
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('bar', this);
    keyboard.setDefaultWindow(null);
  },
  methods: {
    onMouseUp: function(event) {
      if (event.button == 2) {
        var items = [];
        var fullscreen = document.fullscreenElement != null;
        items.push(['Nexti', 'n', this.enable.enable_t]);
        items.push(['Stepi', 's', this.enable.enable_t]);
        items.push(['Continue', 'c', this.enable.enable_t]);
        items.push(['Release suspend', 'r', this.enable.enable_t]);
        items.push(['Fullscreen', 'space', !fullscreen]);
        items.push(['Exit fullscreen', '⎋', fullscreen]);
        this.$menu.alert(event, items, this.onClickMenu);
      }
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
        case 1:
        case 2:
        case 3:
          this.onClickItem(index);
          break;
        case 4:
          if (document.fullscreenElement == null) {
            document.body.webkitRequestFullScreen();
          }
          break;
        case 5:
          if (document.fullscreenElement != null) {
            document.exitFullscreen();
          }
          break;
      }
    },
    onKeyDown: function(event) {
      var d = 0;
      var index = ['n', 's', 'c', 'r'].indexOf(event.key);
      if (index >= 0) {
        if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) {
          return false;
        }
        this.onClickMenu(index + d);
        return true;
      } else {
        d += 4;
        index = [32, 27].indexOf(event.keyCode);
        if (index >= 0) {
          this.onClickMenu(index + d);
          return true;
        } else {
          return false;
        }
      }
    },
    onBreak: function() {
      this.enable.onEnable(true);
    },
    onContinue: function() {
      this.enable.onEnable(false);
    },
    onClickItem: function(index) {
      if (!this.enable.enable_t) {
        return;
      }
      switch (index) {
        case 0:
          asmdb.getInstance().next();
          break;
        case 1:
          asmdb.getInstance().step();
          break;
        case 2:
          asmdb.getInstance().cont();
          break;
        case 3:
          asmdb.getInstance().rlse();
          break;
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.bar-container {
  padding-top: 8px;
  height: 40px;
  display: flex;
  .bar-icon {
    margin-left: 4px;
    width: 32px;
    height: 32px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    background-image: url('/static/icons/folder.png');
  }
  .bar-text {
    margin-right: 4px;
    width: 0px;
    flex-grow: 1;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    line-height: 32px;
    font-size: 16px;
    color: @color-text;
    font-family: 'Wawati SC';
  }
  .bar-item {
    width: 32px;
    height: 32px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    mask-size: 16px 16px;
    mask-repeat: no-repeat;
    mask-position: center center;
    background-color: @color-text-dark;
    cursor: not-allowed;
  }
  .bar-item[css-enable] {
    background-color: transparent;
    cursor: pointer;
  }
  .bar-item[css-enable]:hover {
    border: 4px solid @color-background-dark;
    border-radius: 4px;
    background-color: @color-background-hover;
  }
  .bar-item:last-child {
    margin-right: 4px;
  }
}
</style>
