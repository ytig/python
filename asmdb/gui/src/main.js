import '@/styles/global.less';
import '@/scripts/window';

import Vue from 'vue';
import VueCookies from 'vue-cookies';
Vue.use(VueCookies);
import VueRouter from 'vue-router';
Vue.use(VueRouter);
import VueResource from 'vue-resource';
Vue.use(VueResource);

import editor from '@/plugins/editor';
Vue.use(editor);
import inquiry from '@/plugins/inquiry';
Vue.use(inquiry);
import menu from '@/plugins/menu';
Vue.use(menu);
import progress from '@/plugins/progress';
Vue.use(progress);
import toast from '@/plugins/toast';
Vue.use(toast);

import AnimateButton from '@/views/AnimateButton';
import AssistInput from '@/views/AssistInput';
import Byte from '@/views/Byte';
import Bytes from '@/views/Bytes';
import Comment from '@/views/Comment';
import Gird from '@/views/Gird';
import Indicator from '@/views/Indicator';
import Instruction from '@/views/Instruction';
import Navigation from '@/views/Navigation';
import Navigation2 from '@/views/Navigation2';
import Pager from '@/views/Pager';
import Recycler from '@/views/Recycler';
import Register from '@/views/Register';
import Resize from '@/views/Resize';
import Scroller from '@/views/Scroller';
import Search from '@/views/Search';
import Terminal from '@/views/Terminal';
import Assembly from '@/windows/Assembly';
import Bar from '@/windows/Bar';
import Breakpoints from '@/windows/Breakpoints';
import Memory from '@/windows/Memory';
import Python3 from '@/windows/Python3';
import Registers from '@/windows/Registers';
import Stack from '@/windows/Stack';
import Watchpoints from '@/windows/Watchpoints';
Vue.component('AnimateButton', AnimateButton);
Vue.component('AssistInput', AssistInput);
Vue.component('Byte', Byte);
Vue.component('Bytes', Bytes);
Vue.component('Comment', Comment);
Vue.component('Gird', Gird);
Vue.component('Indicator', Indicator);
Vue.component('Instruction', Instruction);
Vue.component('Navigation', Navigation);
Vue.component('Navigation2', Navigation2);
Vue.component('Pager', Pager);
Vue.component('Recycler', Recycler);
Vue.component('Register', Register);
Vue.component('Resize', Resize);
Vue.component('Scroller', Scroller);
Vue.component('Search', Search);
Vue.component('Terminal', Terminal);
Vue.component('Assembly', Assembly);
Vue.component('Bar', Bar);
Vue.component('Breakpoints', Breakpoints);
Vue.component('Memory', Memory);
Vue.component('Python3', Python3);
Vue.component('Registers', Registers);
Vue.component('Stack', Stack);
Vue.component('Watchpoints', Watchpoints);

import Hello from '@/Hello';
import World from '@/World';
new Vue({
  el: '#app',
  router: new VueRouter({
    routes: [{
      path: '/',
      redirect: '/hello',
    }, {
      path: '/hello',
      component: Hello,
    }, {
      path: '/world',
      component: World,
    }],
  }),
  template: '<router-view v-if="!reloading"/>',
  data: function () {
    return {
      reloading: false
    };
  },
  methods: {
    reload: function () {
      this.reloading = true;
      this.$nextTick(() => {
        this.reloading = false;
      });
    }
  }
});
