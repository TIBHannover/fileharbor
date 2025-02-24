import Vue from 'vue';
import VueRouter from 'vue-router';
import store from '@/store';

Vue.use(VueRouter);
const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'Home',
      component: () => import('@/views/Home.vue'),
    },
    {
      path: '/search',
      name: 'Search',
      component: () => import('@/views/Search.vue'),
    },
    {
      path: '/imprint',
      name: 'Imprint',
      beforeEnter() {
        window.open('https://www.tib.eu/de/impressum', '_blank');
      },
    },
    {
      path: '/privacy',
      name: 'Privacy',
      beforeEnter() {
        window.open('https://www.tib.eu/en/data-protection', '_blank');
      },
    },
    {
      path: '*',
      name: 'NotFound',
      component: () => import('@/views/NotFound.vue'),
    },
  ],
});

const routerPush = VueRouter.prototype.push;
VueRouter.prototype.push = function push(location) {
  return new Promise((resolve, reject) => {
    routerPush.call(this, location, () => {
      resolve(this.currentRoute);
    }, (error) => {
      if (error.name === 'NavigationDuplicated') {
        resolve(this.currentRoute);
      } else {
        reject(error);
      }
    });
  });
};

router.beforeResolve((to, from, next) => {
  if (to.name) {
    const status = { loading: true, error: false };
    store.dispatch('utils/setStatus', status, { root: true });
  }
  next();
});

router.afterEach(() => {
  Vue.nextTick(() => {
    const status = { loading: false, error: false };
    store.dispatch('utils/setStatus', status, { root: true });
  });
});

export default router;
