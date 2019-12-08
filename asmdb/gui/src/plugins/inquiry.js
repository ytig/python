import InquiryVue from '@/plugins/InquiryVue';

export default {
  install: function (Vue) {
    if (Vue.prototype.$inquiry) {
      return;
    }
    var vm = new(Vue.extend(InquiryVue))();
    document.body.appendChild(vm.$mount().$el);
    window.addEventListener('keydown', function (event) {
      if (vm.onKeyDown(event)) {
        event.stopPropagation();
        event.preventDefault();
      }
    }, true);
    Vue.prototype.$inquiry = vm;
  }
};
