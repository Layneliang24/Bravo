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
    {
      path: '/blog',
      name: 'Blog',
      component: (): Promise<Component> => import('../views/Blog.vue'),
    },
    {
      path: '/blog/:id',
      name: 'BlogDetail',
      component: (): Promise<Component> => import('../views/BlogDetail.vue'),
    },
  ],
})

export default router
