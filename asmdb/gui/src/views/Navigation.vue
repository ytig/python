<template>
  <div class="navigation-container" :css-gradient="gradient" @mouseup="onMouseUp">
    <span class="user-select-none" :css-focus="focus" :css-disable="!disable2.bool_f">{{name}}</span>
    <div v-if="gradient" class="navigation-gradient"></div>
  </div>
</template>

<script>
import sloth from '@/scripts/sloth';

export default {
  data: function() {
    return {
      disable2: new sloth(224)
    };
  },
  props: {
    name: String,
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
  methods: {
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
  > span {
    line-height: 40px;
    padding-left: 12px;
    font-size: 16px;
    color: @color-text;
    font-family: 'Wawati SC';
    transition-delay: 1ms;
  }
  > span[css-focus] {
    color: @color-text-light;
  }
  > span[css-disable] {
    text-decoration: line-through;
  }
  .navigation-gradient {
    position: absolute;
    z-index: 1;
    top: 36px;
    width: 100%;
    height: 2px;
    background: linear-gradient(@color-background, transparent);
    pointer-events: none;
  }
}
.navigation-container[css-gradient] {
  height: 36px;
}
</style>
