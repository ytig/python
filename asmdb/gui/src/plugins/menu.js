import MenuVue from '@/plugins/MenuVue';

export default {
  install: function (Vue) {
    if (Vue.prototype.$menu) {
      return;
    }
    var vm = new(Vue.extend(MenuVue))();
    document.body.appendChild(vm.$mount().$el);
    var intercept = false;
    window.addEventListener('mousedown', function (event) {
      if (event.button == 0) {
        intercept = vm.onMouseDown(event);
        if (intercept) {
          event.stopPropagation();
        }
      }
    }, true);
    window.addEventListener('click', function (event) {
      if (intercept) {
        vm.onClick(event);
        event.stopPropagation();
        intercept = false;
      }
    }, true);
    window.addEventListener('contextmenu', function (event) {
      event.preventDefault();
    });
    window.addEventListener('keydown', function (event) {
      if (vm.onKeyDown(event)) {
        event.stopPropagation();
        if (event.keyCode == 9) {
          event.preventDefault();
        }
      }
    }, true);
    window.addEventListener('wheel', function (event) {
      vm.onWheel(event);
    });
    Vue.prototype.$menu = vm;
  }
};
