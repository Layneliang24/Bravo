import { createRouter, createWebHistory } from 'vue-router'
import type { Component } from 'vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Home',
      component: (): Promise<Component> => import('../views/Home.vue'),
    },
    {
      path: '/login',
      name: 'Login',
      component: (): Promise<Component> => import('../views/Login.vue'),
    },
  ],
})

export default router
