export default {
  data: function () {
    return {
      needLayout: [],
      needDraw: ['canvasContext'],
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
      handler: function (newProps) {
        var needLayout = false;
        var needDraw = false;
        if (this.oldProps == null) {
          this.oldProps = Object.assign({}, newProps);
          needLayout = true;
          needDraw = true;
        } else {
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
    draw: function () {
      var cc = this.canvasContext.split(';');
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
