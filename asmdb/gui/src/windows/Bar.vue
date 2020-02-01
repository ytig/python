<template>
  <div class="bar-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <div class="bar-icon" @click="onMouseUp2"></div>
    <div class="bar-grow">
      <span class="bar-text user-select-none" @click="onMouseUp2">{{process}}</span>
    </div>
    <div class="bar-item" v-for="(item, index) in items" :key="index" :title="item.title" :style="item.style" @click="onClickItem(index)" :css-enable="enable.bool_f"></div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';
import sloth from '@/scripts/sloth';
import Hello from '@/Hello';

export default {
  data: function() {
    return {
      enable: new sloth(999),
      process: Hello.getToken(this.$cookies, 'process')
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
        if (this.enable.bool_f) {
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
    requestFocus: function() {
      keyboard.requestFocus(this);
    },
    onMouseUp: function(event) {
      if (event.button == 2) {
        this.onMouseUp2(event);
      }
    },
    onMouseUp2: function(event) {
      var items = [];
      var fullscreen = document.fullscreenElement != null;
      items.push(['Nexti', 'n', this.enable.bool_t]);
      items.push(['Stepi', 's', this.enable.bool_t]);
      items.push(['Continue', 'c', this.enable.bool_t]);
      items.push(['Release suspend', 'r', this.enable.bool_t]);
      items.push(['Fullscreen', '⌃F', !fullscreen]);
      items.push(['Exit fullscreen', '⎋', fullscreen]);
      items.push(['Refresh', '⌘R', true]);
      items.push(['Quit', '⌘E', true]);
      this.$menu.alert(event, items, this.onClickMenu);
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
        case 6:
          this.$root.reload();
          break;
        case 7:
          this.$router.replace('/hello');
          break;
      }
    },
    onKeyDown: function(event) {
      var d = 0;
      var index = ['n', 's', 'c', 'r'].indexOf(event.key);
      if (index >= 0 && !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey) {
        this.onClickMenu(index + d);
        return true;
      } else {
        d += 4;
        index = ['f'].indexOf(event.key);
        if (index >= 0 && !event.altKey && event.ctrlKey && !event.metaKey && !event.shiftKey) {
          this.onClickMenu(index + d);
          return true;
        } else {
          d += 1;
          index = [27].indexOf(event.keyCode);
          if (index >= 0) {
            this.onClickMenu(index + d);
            return true;
          } else {
            d += 1;
            index = ['r', 'e'].indexOf(event.key);
            if (index >= 0 && !event.altKey && !event.ctrlKey && event.metaKey && !event.shiftKey) {
              this.onClickMenu(index + d);
              return true;
            } else {
              return event.keyCode == 9;
            }
          }
        }
      }
    },
    onBreak: function() {
      this.enable.set(true);
    },
    onContinue: function() {
      this.enable.set(false);
    },
    onClickItem: function(index) {
      if (!this.enable.bool_t) {
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
    cursor: context-menu;
  }
  .bar-grow {
    width: 0px;
    flex-grow: 1;
    margin-right: 4px;
    overflow: hidden;
    .bar-text {
      line-height: 32px;
      font-size: 16px;
      color: @color-text;
      font-family: 'Wawati SC';
      cursor: context-menu;
    }
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
