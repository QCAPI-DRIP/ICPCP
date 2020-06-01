import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'
import Ping from '../views/Ping.vue'
import Books from '../views/Books.vue'
import Tosca from '../views/Tosca.vue'
import Wizard from '../components/Wizard.vue'
import Wizardv2 from '../components/Wizardv2.vue'

Vue.use(VueRouter)

  const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/about',
    name: 'About',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/About.vue')
  },
  {
    path: '/courses',
    name: 'Courses',
    // route level code-splitting
    // this generates a separate chunk (about.[hash].js) for this route
    // which is lazy-loaded when the route is visited.
    component: () => import(/* webpackChunkName: "about" */ '../views/Courses.vue')
  },
  {
    path: '/ping',
    name: 'Ping',
    component: Ping
  },

  {
    path: '/books',
    name: 'Books',
    component: Books,
  },

  {
    path: '/tosca',
    name: 'Tosca',
    component: Tosca,
  },

  {
    path: '/wizard',
    name: 'Wizard',
    component: Wizard,
  },

  {
    path: '/wizardv2',
    name: 'Wizardv2',
    component: Wizardv2,
  }

]

const router = new VueRouter({
  routes
})

export default router
