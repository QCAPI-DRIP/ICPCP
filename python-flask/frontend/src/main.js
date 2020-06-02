import Vue from 'vue'
import App from './App.vue'
import router from './router'
import BootstrapVue from 'bootstrap-vue';
import 'bootstrap/dist/css/bootstrap.css';
import VueGoodWizard from 'vue-good-wizard';
import Vuex from "vuex";

Vue.config.productionTip = false
// Vue.use(BootstrapVue);
Vue.use(BootstrapVue);
Vue.use(VueGoodWizard);
Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    count: 0,
    workflow_url: "",
    price_url: "",
    deadline_url: "",
    performance_url: ""

  },
  mutations: {
    increment (state) {
      state.count++
    },
    set_workflow(state, payload) {
      state.workflow_url = payload
    },
    set_price(state, payload) {
      state.price_url = payload
    },
    set_deadline(state, payload) {
      state.deadline_url = payload
    },
    set_performance(state, payload) {
      state.performance_url = payload
    }
  }
})


new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
