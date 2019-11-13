import EditorVue from '@/plugins/EditorVue';

export default {
  install: function (Vue) {
    if (Vue.prototype.$editor) {
      return;
    }
    var vm = new(Vue.extend(EditorVue))();
    document.body.appendChild(vm.$mount().$el);
    //todo
    Vue.prototype.$editor = vm;
  }
};
