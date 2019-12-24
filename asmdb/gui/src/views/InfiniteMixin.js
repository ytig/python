export default {
  data: function () {
    return {
      needLayout: [],
      needDraw: [],
      oldProps: null,
      dirtyLayout: false
    };
  },
  props: {
    canvasContext: String,
    lazyLayout: Boolean
  },
  watch: {
    $props: {
      deep: true,
      immediate: true,
      handler: function callee(newProps) {
        if (this.$el == undefined) {
          this.$nextTick(callee.bind(this, ...arguments));
          return;
        }
        var needLayout = false;
        var needDraw = false;
        if (this.oldProps == null) {
          this.oldProps = Object.assign({}, newProps);
          needLayout = true;
          needDraw = true;
        } else {
          var old_cc = this.oldProps.canvasContext.split(';');
          for (var key in this.oldProps) {
            var oldValue = this.oldProps[key];
            var newValue = newProps[key];
            if (oldValue == newValue) {
              continue;
            }
            this.oldProps[key] = newValue;
            if (this.needLayout.indexOf(key) >= 0) {
              needLayout = true;
              needDraw = true;
            }
            if (this.needDraw.indexOf(key) >= 0) {
              needDraw = true;
            }
          }
        }
        if (!newProps.lazyLayout) {
          if (needLayout || this.dirtyLayout) {
            this.layout();
          }
        } else {
          if (needLayout) {
            this.dirtyLayout = true;
          }
        }
        if (needDraw) {
          this.draw();
        } else {
          var new_cc = newProps.canvasContext.split(';');
          if (old_cc[0] != new_cc[0]) {
            this.draw();
          } else {
            var old_ts = old_cc[1].split(',');
            var new_ts = new_cc[1].split(',');
            var ts = [];
            for (var i of new_ts) {
              if (old_ts.indexOf(i) < 0) {
                ts.push(i);
              }
            }
            if (ts.length > 0) {
              this.draw(new_cc[0] + ';' + ts.join(','));
            }
          }
        }
      }
    }
  },
  methods: {
    layout: function () {
      this.onLayout();
      this.dirtyLayout = false;
    },
    onLayout: function () {},
    draw: function (canvasContext) {
      if (canvasContext == undefined) {
        canvasContext = this.canvasContext;
      }
      var cc = canvasContext.split(';');
      var h = this.onPreDraw();
      var t = parseInt(cc[0]);
      for (var i of cc[1].split(',')) {
        var c = getContext(parseInt(i), t, h);
        if (c != null) {
          this.onDraw(c);
        }
      }
    },
    onPreDraw: function () {
      return 0;
    },
    onDraw: function (ctx) {}
  }
};
