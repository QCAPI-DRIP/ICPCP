import Vue from 'vue'
import App from './App.vue'
import router from './router'
import BootstrapVue from 'bootstrap-vue';
import 'bootstrap/dist/css/bootstrap.css';
import VueGoodWizard from 'vue-good-wizard';
import Vuex from "vuex";
import UploadFileButton from '@/components/UploadFileButton'

Vue.component('upload-file-button', UploadFileButton)
// import vuetify from './plugins/vuetify';

Vue.config.productionTip = false
// Vue.use(BootstrapVue);
Vue.use(BootstrapVue);
Vue.use(VueGoodWizard);
Vue.use(Vuex);

const store = new Vuex.Store({
  state: {
    workflow_url: "",
    price_url: "",
    deadline_url: "",
    performance_url: "",
    workflow_file: null,
    input_file: null

  },
  mutations: {
    set_workflow(state, payload) {
      state.workflow_url = payload
    },
    set_workflow_file(state, payload) {
      state.workflow_file = payload
    },
    set_input_file(state, payload) {
      state.input_file = payload
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
  // vuetify,
  render: h => h(App)
}).$mount('#app')
