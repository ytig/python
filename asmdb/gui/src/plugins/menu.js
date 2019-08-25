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
      intercept = vm.onMouseDown(event);
      if (intercept) {
        event.stopPropagation();
      }
    }, true);
    document.addEventListener('click', function (event) {
      if (intercept) {
        vm.onClick(event);
        event.stopPropagation();
      }
    }, true);
    document.addEventListener('contextmenu', function (event) {
      event.preventDefault();
    });
    Vue.prototype.$menu = vm;
  }
}
