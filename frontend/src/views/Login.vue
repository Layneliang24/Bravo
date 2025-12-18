<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="min-h-screen w-full relative overflow-hidden bg-gradient-to-br from-orange-50 via-yellow-50 to-green-50">
    <!-- 动态渐变背景 -->
    <div class="absolute inset-0">
      <div class="absolute inset-0 bg-gradient-to-br from-orange-100/50 via-yellow-100/30 to-green-100/50" />
      <div
        class="absolute inset-0 bg-gradient-to-tr from-orange-200/20 via-transparent to-green-200/20 animate-pulse-slow"
      />
    </div>

    <!-- 网格背景 -->
    <div class="absolute inset-0 opacity-10">
      <svg width="100%" height="100%">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(249, 115, 22, 0.3)" stroke-width="0.5"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>
    </div>

    <!-- 动态粒子系统 -->
    <div
      v-for="i in 40"
      :key="`particle-${i}`"
      class="absolute rounded-full animate-float"
      :style="{
        width: `${Math.random() * 4 + 1}px`,
        height: `${Math.random() * 4 + 1}px`,
        left: `${Math.random() * 100}%`,
        top: `${Math.random() * 100}%`,
        background: i % 3 === 0
          ? 'rgba(249, 115, 22, 0.4)'
          : i % 3 === 1
          ? 'rgba(234, 179, 8, 0.4)'
          : 'rgba(34, 197, 94, 0.4)',
        boxShadow: `0 0 ${Math.random() * 10 + 5}px ${Math.random() * 3 + 1}px currentColor`,
        animationDelay: `${Math.random() * 5}s`,
        animationDuration: `${Math.random() * 10 + 10}s`
      }"
    />

    <!-- 扫描线效果 -->
    <div class="absolute inset-x-0 h-px bg-gradient-to-r from-transparent via-orange-400 to-transparent opacity-20 animate-scan" />

    <!-- 光晕效果 -->
    <div
      class="absolute top-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl opacity-10 animate-glow"
      style="background: radial-gradient(circle, rgba(249, 115, 22, 0.3), transparent)"
    />

    <div
      class="absolute bottom-1/4 right-1/4 w-96 h-96 rounded-full blur-3xl opacity-10 animate-glow-delayed"
      style="background: radial-gradient(circle, rgba(34, 197, 94, 0.3), transparent)"
    />

    <!-- 浮动的学习元素 -->
    <div
      v-for="(icon, i) in ['📚', '💻', '💼', '✏️']"
      :key="`icon-${i}`"
      class="absolute text-4xl select-none animate-code-float opacity-20"
      :style="{
        left: `${20 + i * 20}%`,
        top: `${10 + i * 15}%`,
        animationDelay: `${i * 0.5}s`,
        animationDuration: `${5 + i}s`
      }"
    >
      {{ icon }}
    </div>

    <!-- 书本装饰 -->
    <div
      v-for="i in 6"
      :key="`book-${i}`"
      class="absolute animate-spin-slow"
      :style="{
        left: `${10 + i * 15}%`,
        top: `${20 + Math.sin(i) * 30}%`,
        animationDuration: `${20 + i * 2}s`,
        animationDelay: `${i * 0.3}s`
      }"
    >
      <svg width="40" height="40" viewBox="0 0 100 100">
        <rect
          x="30" y="20" width="40" height="60"
          fill="none"
          stroke="rgba(249, 115, 22, 0.3)"
          stroke-width="2"
          rx="2"
        />
        <line x1="50" y1="20" x2="50" y2="80" stroke="rgba(249, 115, 22, 0.3)" stroke-width="1"/>
      </svg>
    </div>

    <!-- 主内容区 -->
    <div class="relative z-10 min-h-screen flex items-center justify-center p-4 md:p-8">
      <AuthCard />
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import AuthCard from '@/components/auth/AuthCard.vue'
</script>
