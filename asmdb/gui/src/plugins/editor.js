import EditorVue from '@/plugins/EditorVue';

export default {
  install: function (Vue) {
    if (Vue.prototype.$editor) {
      return;
    }
    var vm = new(Vue.extend(EditorVue))();
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
        event.stopPropagation();
        intercept = false;
      }
    }, true);
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
    Vue.prototype.$editor = vm;
  }
};
