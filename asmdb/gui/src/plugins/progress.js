import ProgressVue from '@/plugins/ProgressVue';

export default {
  install: function (Vue) {
    if (Vue.prototype.$progress) {
      return;
    }
    var vm = new(Vue.extend(ProgressVue))();
    document.body.appendChild(vm.$mount().$el);
    window.addEventListener('keydown', function (event) {
      if (vm.onKeyDown(event)) {
        event.stopPropagation();
        event.preventDefault();
      }
    }, true);
    Vue.prototype.$progress = vm;
  }
};
