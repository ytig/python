export default {
  data: function () {
    return {
      showing: false,
      intercept: false
    };
  },
  created: function () {
    window.addEventListener('mousedown', this.onDomMouseDown, true);
    window.addEventListener('click', this.onDomClick, true);
    window.addEventListener('keydown', this.onDomKeyDown, true);
  },
  destroyed: function () {
    window.removeEventListener('mousedown', this.onDomMouseDown, true);
    window.removeEventListener('click', this.onDomClick, true);
    window.removeEventListener('keydown', this.onDomKeyDown, true);
  },
  methods: {
    show: function () {
      this.showing = true;
      this.onShow();
    },
    onShow: function () {},
    dismiss: function () {
      this.showing = false;
      this.onDismiss();
    },
    onDismiss: function () {},
    onIntercept: function () {
      return true;
    },
    onDomMouseDown: function (event) {
      if (event.button == 0) {
        this.intercept = this.showing && this.onIntercept();
        if (this.intercept) {
          event.stopPropagation();
        }
      }
    },
    onDomClick: function (event) {
      if (this.intercept) {
        event.stopPropagation();
        this.intercept = false;
      }
    },
    onDomKeyDown: function (event) {
      if (this.showing) {
        event.stopPropagation();
        if (event.keyCode == 9) {
          event.preventDefault();
        }
      }
    }
  }
};
