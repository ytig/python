import ToastVue from '@/plugins/ToastVue';

export default {
  install: function (Vue) {
    if (Vue.prototype.$toast) {
      return;
    }
    var vm = new(Vue.extend(ToastVue))();
    document.body.appendChild(vm.$mount().$el);
    Vue.prototype.$toast = vm;
  }
};
