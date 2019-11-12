import '@/styles/global.less';
import '@/scripts/window';

import Vue from 'vue';
import VueRouter from 'vue-router';
Vue.use(VueRouter);

import menu from '@/plugins/menu';
Vue.use(menu);

import Bytes from '@/views/Bytes';
import Gird from '@/views/Gird';
import Indicator from '@/views/Indicator';
import Navigation from '@/views/Navigation';
import Pager from '@/views/Pager';
import Recycler from '@/views/Recycler';
import Register from '@/views/Register';
import Scroller from '@/views/Scroller';
import Search from '@/views/Search';
import Assembly from '@/windows/Assembly';
import Bar from '@/windows/Bar';
import Breakpoints from '@/windows/Breakpoints';
import Memory from '@/windows/Memory';
import Python3 from '@/windows/Python3';
import Registers from '@/windows/Registers';
import Stack from '@/windows/Stack';
import Watchpoints from '@/windows/Watchpoints';
Vue.component('Bytes', Bytes);
Vue.component('Gird', Gird);
Vue.component('Indicator', Indicator);
Vue.component('Navigation', Navigation);
Vue.component('Pager', Pager);
Vue.component('Recycler', Recycler);
Vue.component('Register', Register);
Vue.component('Scroller', Scroller);
Vue.component('Search', Search);
Vue.component('Assembly', Assembly);
Vue.component('Bar', Bar);
Vue.component('Breakpoints', Breakpoints);
Vue.component('Memory', Memory);
Vue.component('Python3', Python3);
Vue.component('Registers', Registers);
Vue.component('Stack', Stack);
Vue.component('Watchpoints', Watchpoints);

import Connect from '@/Connect';
import Debug from '@/Debug';
new Vue({
  el: '#app',
  router: new VueRouter({
    routes: [{
      path: '/',
      redirect: '/connect',
    }, {
      path: '/connect',
      component: Connect,
    }, {
      path: '/debug',
      component: Debug,
    }],
  }),
  template: '<router-view/>',
});
