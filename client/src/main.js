import BootstrapVue from 'bootstrap-vue';
import Vue from 'vue'
import App from './App'
import router from './router'
require('../node_modules/bootstrap/dist/css/bootstrap.css')

Vue.config.productionTip = false
Vue.use(BootstrapVue);

new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
