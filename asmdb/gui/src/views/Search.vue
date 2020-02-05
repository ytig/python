<template>
  <div v-show="showing" class="search-container" :style="{left:containerLeft+'px'}" :css-illegal="illegal" :css-theme="''+theme">
    <div></div>
    <input ref="input" type="text" :style="{width:inputWidth+'px'}" v-model="text" @input="onInput" @keypress="onKeyPress" @blur="dismiss" spellcheck="false" />
  </div>
</template>

<script>
import Animation from '@/scripts/animation';
import asmdb from '@/scripts/asmdb';
import InputMixin from './InputMixin';

function exec(source, locals, condition) {
  if (source.startsWith('/')) {
    source = '__base__ + (' + (source.substring(1) || '0') + ')';
  }
  var result = null;
  try {
    var keys = [];
    var vals = [];
    for (var key in locals) {
      var val = locals[key];
      keys.push(key);
      vals.push(val);
    }
    result = new Function(...keys, 'return ' + source)(...vals);
  } catch (error) {}
  if (typeof result == 'number' && condition(result)) {
    return result;
  } else {
    return null;
  }
}

export default {
  mixins: [InputMixin],
  data: function() {
    return {
      illegal: false,
      text: '',
      realText: '',
      locals: null,
      anim: new Animation(1 / 250)
    };
  },
  props: {
    theme: Number,
    condition: Function
  },
  watch: {
    text: function(newValue, oldValue) {
      if (this.illegal) {
        if (!newValue || exec(newValue, this.locals, this.condition) != null) {
          this.illegal = false;
        }
      }
    }
  },
  computed: {
    inputWidth: function() {
      return Math.ceil(1 + measureText(this.realText));
    },
    containerLeft: function() {
      var input = this.anim.value;
      var K = 0.382;
      var T = 4;
      var output = Math.pow(K, (T * input - 0.25) / (T - 1)) * Math.sin(T * 2 * Math.PI * input);
      return 5 + 10 * output;
    }
  },
  methods: {
    onShow: function() {
      this.locals = asmdb.getInstance().getRegisters();
      var base = asmdb.getInstance().getAddressBase();
      if (base != null) {
        this.locals.__base__ = base;
      }
      this.text = '';
      this.realText = '';
      this.anim.$value(0);
      this.$nextTick(() => {
        this.$refs.input.focus();
      });
    },
    onDismiss: function() {
      this.locals = null;
    },
    onInput: function() {
      this.realText = this.$refs.input.value;
    },
    onKeyPress: function(event) {
      if (event.keyCode == 13) {
        if (!this.text) {
          this.dismiss();
        } else {
          var result = exec(this.text, this.locals, this.condition);
          if (result != null) {
            this.$emit('search', result);
            this.dismiss();
          } else {
            this.illegal = true;
            this.anim.$value(0);
            this.anim.$target(1);
          }
        }
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.search-container {
  position: absolute;
  z-index: 4;
  left: 5px;
  top: 5px;
  border-radius: 2px;
  box-shadow: 1px 1px @color-border-shadow;
  > div {
    position: absolute;
    left: 2px;
    top: 3px;
    width: 16px;
    height: 16px;
    pointer-events: none;
  }
  > input {
    box-sizing: content-box;
    border-radius: 2px;
    border: 1px solid transparent;
    padding: 3px 3px 1px 20px;
    max-width: 224px;
    line-height: 14px;
    font-size: 12px;
    color: @color-text-light;
  }
  > input::selection {
    background: @color-background-selection2;
  }
}
.search-container[css-illegal] {
  > input {
    border: 1px solid @color-border-illegal;
  }
}
.search-container[css-theme='0'] {
  background: @color-background-popup;
  > div {
    background-image: url('/static/icons/search.png');
  }
}
.search-container[css-theme='1'] {
  background: @color-background-popup2;
  > div {
    background-image: url('/static/icons/edit.png');
  }
}
</style>
