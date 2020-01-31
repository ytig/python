<template>
  <div ref="container" class="terminal-container"></div>
</template>

<script>
import 'xterm/css/xterm.css';
import { Terminal } from 'xterm';
import asmdb from '@/scripts/asmdb';
import Theme from '@/styles/theme';
const WIDTH0 = 7;
const HEIGHT0 = 16;

function write_lazy_bell(terminal, utf8) {
  terminal.write(utf8);
  if (!terminal._bell) {
    terminal._bell = true;
    setTimeout(() => {
      terminal.setOption('bellStyle', 'sound');
      terminal.setOption('bellSound', 'data:audio/mp3;base64,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');
    });
  }
}

export default {
  data: function() {
    return {
      terminal: null
    };
  },
  props: {
    focus: Boolean,
    utf8: String
  },
  watch: {
    focus: function(newValue) {
      if (newValue) {
        this.terminal.focus();
      } else {
        this.terminal.clearSelection();
        this.terminal.blur();
      }
    },
    utf8: function(newValue, oldValue) {
      write_lazy_bell(this.terminal, newValue.substring(oldValue.length));
    }
  },
  mounted: function() {
    this.terminal = new Terminal({
      allowTransparency: true,
      fontSize: 12,
      fontFamily: 'Menlo',
      lineHeight: HEIGHT0 / 14,
      theme: {
        foreground: Theme.colorText,
        background: 'transparent',
        cursor: Theme.colorText,
        selection: Theme.colorBackgroundSelection,
        black: Theme.colorBackground,
        red: Theme.colorText2,
        green: Theme.colorText5,
        yellow: Theme.colorText4,
        blue: Theme.colorText3,
        magenta: Theme.colorBackgroundPopup2,
        cyan: Theme.colorBackgroundPopup,
        white: Theme.colorText,
        brightBlack: Theme.colorBackground,
        brightRed: Theme.colorText2,
        brightGreen: Theme.colorText5,
        brightYellow: Theme.colorText4,
        brightBlue: Theme.colorText3,
        brightMagenta: Theme.colorBackgroundPopup2,
        cybrightCyanan: Theme.colorBackgroundPopup,
        brightWhite: Theme.colorText
      }
    });
    this.terminal.open(this.$refs.container);
    this.terminal.onData(this.onData);
    this.terminal.textarea.addEventListener('blur', this.onBlur);
    if (this.utf8) {
      write_lazy_bell(this.terminal, this.utf8);
    }
    this.terminal.focus();
    if (!this.focus) {
      this.terminal.blur();
    }
  },
  destroyed: function() {
    this.terminal.textarea.removeEventListener('blur', this.onBlur);
    this.terminal.dispose();
  },
  methods: {
    clearBy: function(sep) {
      if (this.utf8) {
        write_lazy_bell(this.terminal, '\x1bc' + this.utf8.substring(this.utf8.lastIndexOf(sep)).replace(/\x07/g, ''));
      }
    },
    setWindowSize: function(rows, cols) {
      this.terminal.resize(cols, rows);
    },
    onData: function(utf8) {
      asmdb.getInstance().writeu(utf8);
    },
    onBlur: function() {
      if (this.focus) {
        this.terminal.focus();
      }
    }
  }
};
</script>

<style lang="less">
@import '~@/styles/theme';

.terminal-container {
  padding: 0px 12px;
  overflow: hidden;
}
.xterm-helper-textarea {
  font-size: 12px;
}
</style>
