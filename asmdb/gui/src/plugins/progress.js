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
        if (['x', 'c', 'v', 'a'].indexOf(event.key) < 0 || !event.metaKey) {
          event.preventDefault();
        }
      }
    }, true);
    Vue.prototype.$progress = vm;
  }
};
