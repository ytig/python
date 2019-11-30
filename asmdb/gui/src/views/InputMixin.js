export default {
  data: function () {
    return {
      showing: false,
      intercept: false
    };
  },
  created: function () {
    document.addEventListener('mousedown', this.onDomMouseDown, true);
    document.addEventListener('click', this.onDomClick, true);
    document.addEventListener('keydown', this.onDomKeyDown, true);
  },
  destroyed: function () {
    document.removeEventListener('mousedown', this.onDomMouseDown, true);
    document.removeEventListener('click', this.onDomClick, true);
    document.removeEventListener('keydown', this.onDomKeyDown, true);
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
