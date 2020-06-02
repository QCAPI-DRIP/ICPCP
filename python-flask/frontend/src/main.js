import Vue from 'vue'
import App from './App.vue'
import router from './router'
import BootstrapVue from 'bootstrap-vue';
import 'bootstrap/dist/css/bootstrap.css';
import VueGoodWizard from 'vue-good-wizard';

Vue.config.productionTip = false
// Vue.use(BootstrapVue);
Vue.use(BootstrapVue);
Vue.use(VueGoodWizard);

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
