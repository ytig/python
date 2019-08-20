import "@/styles/global.less";

import Vue from 'vue';
import VueRouter from 'vue-router';
Vue.use(VueRouter);

import Gird from '@/views/Gird'
import Title from "@/views/Title";
import Assembly from "@/windows/Assembly";
import Bar from "@/windows/Bar";
import Breakpoints from "@/windows/Breakpoints";
import Memory from "@/windows/Memory";
import Python3 from "@/windows/Python3";
import Registers from "@/windows/Registers";
import Stack from "@/windows/Stack";
import Watchpoints from "@/windows/Watchpoints";
Vue.component("Gird", Gird);
Vue.component("Title", Title);
Vue.component("Assembly", Assembly);
Vue.component("Bar", Bar);
Vue.component("Breakpoints", Breakpoints);
Vue.component("Memory", Memory);
Vue.component("Python3", Python3);
Vue.component("Registers", Registers);
Vue.component("Stack", Stack);
Vue.component("Watchpoints", Watchpoints);

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
