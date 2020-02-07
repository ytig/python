<template>
  <div class="breakpoints-container" @wheel.passive="requestFocus" @mousedown="requestFocus" @mouseup="onMouseUp">
    <Search ref="search" :theme="1" :condition="searchTest" @search="onAddPoint"></Search>
    <Navigation :name="'Bpoints'" :focus="focus" :gradient="true" @mouseup2="onMouseUp2"></Navigation>
    <div class="breakpoints-layout">
      <div></div>
      <div class="breakpoints-item" v-for="point in breakpoints" :key="point.address" :css-disable="point.disable">
        <span></span>
        <span @click="onClickItem(point)" @mouseup="onMouseUpItem(point, ...arguments)">{{toHex(point.address)}}</span>
        <Comment ref="comments" class="breakpoints-grow" :value="point.comment" @input="onCommentPoint(point, arguments[0])"></Comment>
        <div class="breakpoints-icon" @click="commentPoint"></div>
        <div class="breakpoints-icon" @click="onTogglePoint(point)"></div>
        <div class="breakpoints-icon" @click="onSubPoint(point)"></div>
      </div>
      <div class="breakpoints-func">
        <div class="breakpoints-icon" @click="onClickMenu(1)"></div>
      </div>
      <div></div>
    </div>
  </div>
</template>

<script>
import keyboard from '@/scripts/keyboard';
import asmdb from '@/scripts/asmdb';

export default {
  data: function() {
    return {
      focus: false,
      breakpoints: []
    };
  },
  mounted: function() {
    keyboard.registerWindow(this);
    asmdb.getInstance().registerEvent('breakpoints', this);
  },
  destroyed: function() {
    asmdb.getInstance().unregisterEvent('breakpoints', this);
    keyboard.unregisterWindow(this);
  },
  methods: {
    toHex: function(address) {
      return '0x' + address.toString(16).zfill(2 * asmdb.getInstance().UNIT);
    },
    searchTest: function(address) {
      var range = asmdb.getInstance().getAssemblyRange();
      return address >= range[0] && address < range[1];
    },
    requestFocus: function() {
      keyboard.requestFocus(this);
    },
    onFocusChanged: function(value) {
      this.focus = value;
      if (!value) {
        this.$refs.search.dismiss();
        for (var comment of this.$refs.comments || []) {
          comment.dismiss();
        }
      }
    },
    onMouseUp: function(event) {
      if (event.button == 2) {
        this.$menu.close();
      }
    },
    onMouseUp2: function(evnet) {
      var items = [];
      items.push(['Delete all', '⇧⌫', this.breakpoints.length > 0]);
      items.push(['Edit breakpoint', '↩︎', true]);
      this.$menu.alert(event, items, this.onClickMenu);
    },
    onClickMenu: function(index) {
      switch (index) {
        case 0:
          if (this.breakpoints.length > 0) {
            asmdb.getInstance().bpt(this.breakpoints, []);
          }
          break;
        case 1:
          this.$refs.search.show();
          break;
      }
    },
    onKeyDown: function(event) {
      var d = 0;
      var index = [8].indexOf(event.keyCode);
      if (index >= 0 && !event.altKey && !event.ctrlKey && !event.metaKey && event.shiftKey) {
        this.onClickMenu(index + d);
        return true;
      } else {
        d += 1;
        index = [13].indexOf(event.keyCode);
        if (index >= 0) {
          this.onClickMenu(index + d);
          return true;
        } else {
          return false;
        }
      }
    },
    onBreakpoints: function(breakpoints) {
      this.breakpoints.splice(0, this.breakpoints.length, ...breakpoints);
      this.breakpoints.sort((p1, p2) => {
        return p1.address - p2.address;
      });
    },
    onClickItem: function(point) {
      this.$emit('clickitem', 0, point.address);
    },
    onSubPoint: function(point) {
      asmdb.getInstance().bpt([point], []);
    },
    onTogglePoint: function(point) {
      point = Object.assign({}, point);
      point.disable = !point.disable;
      asmdb.getInstance().bpt([], [point]);
    },
    commentPoint: function(event) {
      for (var comment of this.$refs.comments || []) {
        if (comment.$el.parentNode.contains(event.target)) {
          comment.selectEnd();
          comment.show();
          break;
        }
      }
    },
    onCommentPoint: function(point, comment) {
      point = Object.assign({}, point);
      point.comment = comment;
      asmdb.getInstance().bpt([], [point]);
    },
    onAddPoint: function(address) {
      asmdb.getInstance().bpt([], [{ address: address, disable: false, comment: '' }]);
    },
    onMouseUpItem: function(point, event) {
      if (event.button == 2) {
        var menu = this.onCreateMenu(point);
        this.$menu.alert(event, menu, i => {
          menu[i].event();
        });
        event.stopPropagation();
      }
    },
    onCreateMenu: function(point) {
      var items = [];
      var intValue = point.address;
      items.push(['Copy', '', true]);
      items[items.length - 1].event = () => {
        emptySelection();
        this.$toast.alert('Text Copied');
        copyText('0x' + intValue.toString(16));
      };
      return items;
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.breakpoints-container {
  position: relative;
  height: 157px;
  display: flex;
  flex-direction: column;
  .breakpoints-layout {
    height: 0px;
    flex-grow: 1;
    overflow-y: scroll;
    padding-left: 12px;
    padding-right: 12px;
    > div:first-child {
      height: 4px;
    }
    > div:last-child {
      height: 9px;
    }
    .breakpoints-item {
      height: 18px;
      display: flex;
      align-items: center;
      > span:nth-of-type(1) {
        width: 5px;
        height: 5px;
        border-radius: 999px;
        background: @color-icon-breakpoint;
        margin-right: 8px;
      }
      > span:nth-of-type(2) {
        font-size: 12px;
        color: @color-text;
        cursor: pointer;
        margin-right: 8px;
      }
      .breakpoints-grow {
        flex-grow: 1;
      }
      .breakpoints-icon {
        margin-left: 12px;
      }
      .breakpoints-icon:nth-last-of-type(1) {
        background-image: url('/static/icons/sub.png');
      }
      .breakpoints-icon:nth-last-of-type(2) {
        background-image: url('/static/icons/toggle.png');
      }
      .breakpoints-icon:nth-last-of-type(3) {
        background-image: url('/static/icons/comment.png');
        margin-left: 8px;
      }
    }
    .breakpoints-item[css-disable] {
      > span:nth-of-type(1) {
        background: @color-icon-breakpoint2;
      }
      > span:nth-of-type(2) {
        color: @color-text-dark;
        text-decoration: line-through;
      }
    }
    .breakpoints-func {
      display: flex;
      flex-direction: row-reverse;
      align-items: center;
      > div {
        margin-left: 12px;
        margin-top: 1px;
        margin-bottom: 1px;
      }
      > div:nth-of-type(1) {
        background-image: url('/static/icons/add.png');
      }
    }
  }
  .breakpoints-icon {
    width: 16px;
    height: 16px;
    background-size: 16px 16px;
    background-repeat: no-repeat;
    background-position: center center;
    cursor: pointer;
  }
}
</style>
