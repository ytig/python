<template>
  <div class="navigation-container" :css-gradient="gradient" @mouseup="onMouseUp">
    <span class="user-select-none" :css-focus="focus" :css-disable="!disable2.bool_f" @click="onClick">{{name}}</span>
    <div class="navigation-grow">
      <span v-for="(item, index) in labels" :key="index">{{item}}</span>
    </div>
    <div v-if="gradient" class="navigation-gradient" :style="{background:'linear-gradient('+backgroundColor+', transparent)'}"></div>
  </div>
</template>

<script>
import sloth from '@/scripts/sloth';

export default {
  data: function() {
    return {
      disable2: new sloth(999),
      backgroundColor: 'transparent'
    };
  },
  props: {
    name: String,
    label: String,
    focus: Boolean,
    disable: Boolean,
    gradient: Boolean
  },
  watch: {
    disable: {
      immediate: true,
      handler: function(newValue) {
        this.disable2.set(!newValue);
      }
    }
  },
  computed: {
    labels: function() {
      return (this.label || '').split('|').filter(item => item);
    }
  },
  mounted: function() {
    this.backgroundColor = getBackgroundColor(this.$el);
  },
  methods: {
    onClick: function(event) {
      this.$emit('mouseup2', event);
    },
    onMouseUp: function(event) {
      if (event.button == 2) {
        this.$emit('mouseup2', event);
        event.stopPropagation();
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.navigation-container {
  position: relative;
  height: 40px;
  display: flex;
  align-items: flex-start;
  > span {
    margin: 9px 12px 0px 12px;
    font-size: 16px;
    font-family: 'Wawati SC';
    color: @color-text;
    transition-delay: 1ms;
    cursor: context-menu;
  }
  > span[css-focus] {
    color: @color-text-light;
  }
  > span[css-disable] {
    text-decoration: line-through;
  }
  .navigation-grow {
    width: 0px;
    flex-grow: 1;
    display: flex;
    justify-content: flex-end;
    overflow: hidden;
    > span {
      margin: 9px 12px 0px 0px;
      font-size: 14px;
      font-family: 'Wawati SC';
      color: @color-text;
    }
  }
  .navigation-gradient {
    position: absolute;
    z-index: 1;
    top: 36px;
    width: 100%;
    height: 2px;
    pointer-events: none;
  }
}
.navigation-container[css-gradient] {
  height: 36px;
}
</style>
