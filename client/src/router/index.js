import Vue from 'vue'
import Router from 'vue-router'
import Home from '@/components/Home'
import Login from '@/components/Login'
import Register from '@/components/Register'
import Profile from '@/components/Profile'
import Files from '@/components/Files'

import AdminUsers from '@/components/AdminUsers'
import AdminFiles from '@/components/AdminFiles'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },
    {
      path: '/login',
      name: 'Login',
      component: Login
    },
    {
      path: '/register',
      name: 'Register',
      component: Register
    },
    {
      path: '/profile',
      name: 'Profile',
      component: Profile
    },
	{
      path: '/files',
      name: 'Files',
      component: Files
    },
	{
      path: '/adminusers',
      name: 'AdminUsers',
      component: AdminUsers
    },

	{
      path: '/adminfiles',
      name: 'AdminFiles',
      component: AdminFiles
    }
  ],
    mode: 'history',
})
