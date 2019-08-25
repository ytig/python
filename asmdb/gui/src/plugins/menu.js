import MenuVue from '@/plugins/MenuVue';

export default {
  install: function (Vue) {
    if (Vue.prototype.$menu) {
      return;
    }
    $(document).bind("contextmenu", function () {
      return false;
    });
    var vm = new(Vue.extend(MenuVue))();
    document.body.appendChild(vm.$mount().$el);
    document.body.addEventListener('mousedown', (event) => {
      vm.onMouseDown(event);
    });
    Vue.prototype.$menu = vm;
  }
}
