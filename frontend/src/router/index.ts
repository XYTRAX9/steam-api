import { createRouter, createWebHistory } from 'vue-router'
import Home from '@/views/Home.vue'
import Games from '@/views/Games.vue'
import Status from '@/views/Status.vue'
import Callback from '@/views/Callback.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home,
    },
    {
      path: '/games',
      name: 'games',
      component: Games,
    },
    {
      path: '/status',
      name: 'status',
      component: Status,
    },
    {
      path: '/auth/callback',
      name: 'callback',
      component: Callback,
    },
  ],
})

export default router
