import EditorVue from '@/plugins/EditorVue';

export default {
  install: function (Vue) {
    if (Vue.prototype.$editor) {
      return;
    }
    var vm = new(Vue.extend(EditorVue))();
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
      }
    }, true);
    document.addEventListener('wheel', function (event) {
      vm.onWheel(event);
    });
    Vue.prototype.$editor = vm;
  }
};
