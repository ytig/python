import '@/styles/global.css';

import Vue from 'vue';
import VueRouter from 'vue-router';

import Connect from './Connect';
import Debug from './Debug';

Vue.use(VueRouter);
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
