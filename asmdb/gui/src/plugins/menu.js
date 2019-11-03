import MenuVue from '@/plugins/MenuVue';

export default {
  install: function (Vue) {
    if (Vue.prototype.$menu) {
      return;
    }
    var vm = new(Vue.extend(MenuVue))();
    document.body.appendChild(vm.$mount().$el);
    var intercept = false;
    document.addEventListener('mousedown', function (event) {
      if (event.button == 0) {
        intercept = vm.onMouseDown(event);
        if (intercept) {
          event.stopPropagation();
        }
      }
    }, true);
    document.addEventListener('click', function (event) {
      if (intercept) {
        vm.onClick(event);
        event.stopPropagation();
        intercept = false;
      }
    }, true);
    document.addEventListener('contextmenu', function (event) {
      event.preventDefault();
    });
    document.addEventListener('keydown', function (event) {
      if (vm.onKeyDown(event)) {
        event.stopPropagation();
        event.preventDefault();
      }
    }, true);
    document.addEventListener('wheel', function (event) {
      vm.onWheel(event);
    });
    Vue.prototype.$menu = vm;
  }
};
