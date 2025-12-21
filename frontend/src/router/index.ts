// REQ-ID: REQ-2025-003-user-login
import type { Component } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

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
    {
      path: '/register',
      name: 'Register',
      component: (): Promise<Component> => import('../views/Register.vue'),
    },
    {
      path: '/forgot-password',
      name: 'ForgotPassword',
      component: (): Promise<Component> =>
        import('../views/ForgotPasswordView.vue'),
    },
    {
      path: '/reset-password',
      name: 'ResetPassword',
      component: (): Promise<Component> =>
        import('../views/ResetPasswordView.vue'),
    },
    {
      path: '/verify-email',
      name: 'VerifyEmail',
      component: (): Promise<Component> =>
        import('../views/VerifyEmailView.vue'),
    },
  ],
})

export default router
