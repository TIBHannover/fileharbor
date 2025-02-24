import Vue from 'vue';
import VueIntro from 'vue-introjs';
import AsyncComputed from 'vue-async-computed';
import i18n from '@/plugins/i18n';
import vuetify from '@/plugins/vuetify';
import App from '@/App.vue';
import store from '@/store';
import router from '@/router';
import mixins from '@/mixins';
import 'intro.js/introjs.css';
import '@/styles/custom.css';
import '@/styles/introjs.css';

Vue.use(VueIntro);
Vue.use(AsyncComputed);
Vue.mixin(mixins);

const IART = Vue.extend({
  created() {
    this.$store.dispatch('user/getCSRFToken').then(() => {
      this.$store.dispatch('user/getUserData');
      setTimeout(
        () => this.$store.dispatch('api/setState', this.$route.query),
        500,
      );
    });
  },
  watch: {
    '$store.state.user.loggedIn': function () {
      this.$store.dispatch('collection/list');
      this.$store.dispatch('bookmark/list');
    },
  },
});

new IART({
  vuetify,
  router,
  store,
  i18n,
  render: (h) => h(App),
})
  .$mount('#app');
