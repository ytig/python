export default {
  data: function () {
    return {
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
      handler: function (newProps) {
        var needLayout = false;
        var needDraw = false;
        if (this.oldProps == null) {
          needLayout = true;
          needDraw = true;
        } else {
          for (var key in this.oldProps) {
            var oldValue = this.oldProps[key];
            var newValue = newProps[key];
            if (oldValue == newValue || JSON.stringify(oldValue) == JSON.stringify(newValue)) {
              continue;
            }
            switch (key) {
              case 'canvasContext':
                needDraw = true;
                break;
              case 'lazyLayout':
                break;
              default:
                if (key.endsWith('__')) {} else if (key.endsWith('_')) {
                  needDraw = true;
                } else {
                  needDraw = true;
                  needLayout = true;
                }
                break;
            }
          }
        }
        this.oldProps = Object.assign({}, newProps);
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
  mounted: function () {
    if (!this.lazyLayout) {
      this.layout();
    } else {
      this.dirtyLayout = true;
    }
    this.draw();
  },
  methods: {
    layout: function () {
      this.onLayout();
      this.dirtyLayout = false;
    },
    onLayout: function () {},
    draw: function () {
      var cc = this.canvasContext.split(';');
      var h = 18; //todo
      var t = parseInt(cc[0]);
      for (var i of cc[1].split(',')) {
        var c = getContext(parseInt(i), t, h);
        if (c != null) {
          this.onDraw(c);
        }
      }
    },
    onDraw: function (ctx) {}
  }
};
