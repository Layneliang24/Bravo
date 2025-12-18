<!-- REQ-ID: REQ-2025-003-user-login -->
<!-- 直接使用Figma源代码，保持一致性便于调试 -->
<template>
  <div class="w-full max-w-6xl fade-in">
    <!-- 主容器 - 明亮学习风格 -->
    <div
      class="relative rounded-2xl overflow-hidden shadow-2xl"
      style="
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(30px) saturate(150%);
        -webkit-backdrop-filter: blur(30px) saturate(150%);
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow:
          0 8px 32px rgba(249, 115, 22, 0.1),
          0 0 0 1px rgba(249, 115, 22, 0.1),
          inset 0 0 60px rgba(255, 255, 255, 0.3);
      "
      data-testid="auth-card"
    >
      <!-- 顶部发光边框 -->
      <div
        class="absolute top-0 left-0 right-0 h-1"
        style="
          background: linear-gradient(
            90deg,
            rgba(249, 115, 22, 0.5),
            rgba(234, 179, 8, 0.5),
            rgba(34, 197, 94, 0.5),
            rgba(249, 115, 22, 0.5)
          );
        "
      />

      <!-- 角落装饰 -->
      <div
        class="absolute top-0 left-0 w-20 h-20 border-l-2 border-t-2 border-orange-400/40"
      />
      <div
        class="absolute top-0 right-0 w-20 h-20 border-r-2 border-t-2 border-yellow-400/40"
      />
      <div
        class="absolute bottom-0 left-0 w-20 h-20 border-l-2 border-b-2 border-green-400/40"
      />
      <div
        class="absolute bottom-0 right-0 w-20 h-20 border-r-2 border-b-2 border-orange-400/40"
      />

      <div class="grid md:grid-cols-5 min-h-[680px]">
        <!-- 左侧 - 学习装饰区 -->
        <div
          class="relative hidden md:block md:col-span-2 p-12 border-r-2 border-orange-100"
        >
          <!-- 背景动画网格 -->
          <div class="absolute inset-0 opacity-5">
            <svg width="100%" height="100%">
              <defs>
                <pattern
                  id="smallGrid"
                  width="20"
                  height="20"
                  patternUnits="userSpaceOnUse"
                >
                  <path
                    d="M 20 0 L 0 0 0 20"
                    fill="none"
                    stroke="rgba(249, 115, 22, 0.5)"
                    stroke-width="0.5"
                  />
                </pattern>
              </defs>
              <rect width="100%" height="100%" fill="url(#smallGrid)" />
            </svg>
          </div>

          <div class="relative h-full flex flex-col justify-between">
            <!-- 标题区 -->
            <div class="slide-in-left">
              <div class="flex items-center gap-3 mb-6">
                <div
                  class="p-2 bg-gradient-to-br from-orange-400 to-yellow-400 rounded-xl shadow-lg"
                >
                  <svg
                    class="w-8 h-8 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
                    />
                  </svg>
                </div>
                <div>
                  <h2 class="text-gray-800 tracking-wide text-2xl font-bold">
                    Learning Hub
                  </h2>
                  <p class="text-orange-500 text-sm font-medium">
                    Grow Every Day
                  </p>
                </div>
              </div>
              <p class="text-gray-600 leading-relaxed mb-8">
                Welcome to your personal learning space for English, Coding, and
                Career Growth
              </p>
            </div>

            <!-- 中间 - 学习图标展示 -->
            <div class="flex-1 flex items-center justify-center">
              <div class="relative w-64 h-64">
                <!-- 中心圆环 -->
                <div
                  class="absolute inset-0 rounded-full border-4 border-orange-200 animate-spin-slow"
                />

                <!-- 外圆环 -->
                <div
                  class="absolute inset-[-20px] rounded-full border-2 border-yellow-200 animate-spin-reverse"
                />

                <!-- 学习图标环绕 - 使用transform rotate实现真正的环绕效果 -->
                <!-- 重要：z-index设置为10，确保图标显示在装饰圆点（z-index: 1）上面 -->
                <div
                  v-for="(item, i) in learningIcons"
                  :key="`icon-${i}`"
                  class="absolute w-16 h-16 bg-gradient-to-br rounded-2xl shadow-lg flex items-center justify-center"
                  :class="item.gradient"
                  :style="{
                    left: '50%',
                    top: '50%',
                    marginLeft: '-32px',
                    marginTop: '-32px',
                    transform: `rotate(${(i * 360) / 3}deg) translateX(120px) rotate(${-(i * 360) / 3}deg)`,
                    animation: `orbit-rotate 4s ease-in-out infinite`,
                    animationDelay: `${i * 0.3}s`,
                    zIndex: 10,
                  }"
                >
                  <component :is="item.icon" class="w-8 h-8 text-white" />
                </div>

                <!-- 中心图标 - 灯泡图标，带变大变小动画 -->
                <!-- 重要：z-index设置为20，确保中心图标显示在最上层 -->
                <div
                  class="absolute inset-0 flex items-center justify-center"
                  style="z-index: 20"
                >
                  <div
                    class="p-6 bg-gradient-to-br from-orange-400 to-yellow-400 rounded-3xl shadow-2xl animate-bulb-pulse"
                  >
                    <svg
                      class="w-16 h-16 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
                      />
                    </svg>
                  </div>
                </div>

                <!-- 装饰圆点 -->
                <!-- 重要：z-index设置为1，确保圆点显示在图标（z-index: 10）下面 -->
                <div
                  v-for="i in 8"
                  :key="`dot-${i}`"
                  class="absolute w-3 h-3 rounded-full bg-gradient-to-r from-orange-400 to-yellow-400 animate-ping-slow"
                  :style="{
                    left: `${50 + Math.cos((i * Math.PI) / 4) * 40}%`,
                    top: `${50 + Math.sin((i * Math.PI) / 4) * 40}%`,
                    animationDelay: `${i * 0.2}s`,
                    zIndex: 1,
                  }"
                />
              </div>
            </div>

            <!-- 底部特性 -->
            <div class="space-y-4 slide-in-left delay-400">
              <div
                v-for="(item, index) in features"
                :key="index"
                class="flex items-center gap-4 p-3 rounded-xl bg-gradient-to-r hover:shadow-md transition-all cursor-pointer group"
                :class="item.bgGradient"
              >
                <div :class="`p-2 rounded-lg ${item.iconBg}`">
                  <component :is="item.icon" class="w-5 h-5 text-white" />
                </div>
                <div>
                  <p class="text-gray-800 font-semibold text-sm">
                    {{ item.title }}
                  </p>
                  <p class="text-gray-600 text-xs">{{ item.desc }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧 - 表单区域 -->
        <div
          class="md:col-span-3 p-10 md:p-14 flex flex-col justify-center bg-white/50"
          data-testid="form-section"
        >
          <!-- 头像预览区域 -->
          <transition name="avatar">
            <div v-if="showAvatar" class="mb-10">
              <div
                class="flex items-center gap-5 p-5 rounded-2xl bg-gradient-to-r from-orange-50 to-yellow-50 border-2 border-orange-200 shadow-lg"
              >
                <!-- 头像 -->
                <div
                  class="relative scale-in"
                  style="width: 80px; height: 80px"
                >
                  <!-- 扫描圆环 - 以头像中心为旋转中心 -->
                  <svg
                    class="absolute w-24 h-24"
                    style="
                      left: 50%;
                      top: 50%;
                      transform: translate(-50%, -50%);
                    "
                    viewBox="0 0 100 100"
                  >
                    <circle
                      cx="50"
                      cy="50"
                      r="48"
                      fill="none"
                      stroke="url(#gradient-ring)"
                      stroke-width="3"
                      stroke-dasharray="10 5"
                      class="animate-spin"
                      style="transform-origin: 50px 50px"
                    />
                    <defs>
                      <linearGradient
                        id="gradient-ring"
                        x1="0%"
                        y1="0%"
                        x2="100%"
                        y2="100%"
                      >
                        <stop
                          offset="0%"
                          style="stop-color: rgb(249, 115, 22); stop-opacity: 1"
                        />
                        <stop
                          offset="100%"
                          style="stop-color: rgb(34, 197, 94); stop-opacity: 1"
                        />
                      </linearGradient>
                    </defs>
                  </svg>

                  <!-- 外发光 -->
                  <div
                    class="absolute -inset-1 rounded-full bg-orange-300/40 blur-md animate-pulse"
                  />

                  <!-- 头像本体 -->
                  <div
                    class="absolute w-20 h-20 rounded-full overflow-hidden border-4 border-white shadow-lg"
                    style="
                      left: 50%;
                      top: 50%;
                      transform: translate(-50%, -50%);
                    "
                  >
                    <img
                      :src="avatarUrl"
                      alt="Avatar"
                      class="w-full h-full object-cover"
                    />
                  </div>

                  <!-- 验证标记 -->
                  <div
                    class="absolute -bottom-1 -right-1 w-8 h-8 bg-gradient-to-br from-green-400 to-emerald-500 rounded-full flex items-center justify-center border-4 border-white shadow-lg scale-in delay-300"
                  >
                    <svg
                      class="w-4 h-4 text-white"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="3"
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                </div>

                <!-- 欢迎信息 -->
                <div class="flex-1 slide-in-right delay-200">
                  <div class="flex items-center gap-2 mb-1">
                    <svg
                      class="w-5 h-5 text-green-500"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <p class="text-green-600 font-semibold">Account Verified</p>
                  </div>
                  <p class="text-gray-700">
                    Welcome back,
                    <span class="text-orange-600 font-bold">{{
                      displayName
                    }}</span>
                  </p>
                  <p class="text-gray-500 text-sm mt-1">
                    Ready to continue learning?
                  </p>
                </div>

                <!-- 状态指示器 -->
                <div class="flex flex-col gap-2">
                  <div
                    class="w-3 h-3 bg-green-400 rounded-full animate-pulse shadow-lg"
                  />
                  <div class="w-3 h-3 bg-orange-200 rounded-full" />
                  <div class="w-3 h-3 bg-yellow-200 rounded-full" />
                </div>
              </div>
            </div>
          </transition>

          <!-- 表单头部 -->
          <div class="mb-10 fade-in">
            <h2
              class="mb-2 tracking-wide text-3xl font-bold"
              style="color: #1e2939"
            >
              Welcome Back
            </h2>
            <p class="form-subtitle" style="color: #4a5565">
              Continue your learning journey
            </p>
          </div>

          <!-- 登录表单 -->
          <LoginForm
            @preview-success="handlePreviewSuccess"
            @preview-clear="handlePreviewClear"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { ref } from 'vue'
import LoginForm from './LoginForm.vue'

// 学习图标组件
const BookIcon = {
  template:
    '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" /></svg>',
}
const CodeIcon = {
  template:
    '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" /></svg>',
}
const BriefcaseIcon = {
  template:
    '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>',
}

const showAvatar = ref(false)
const displayName = ref('')
const avatarUrl = ref('')

const learningIcons = [
  { icon: BookIcon, gradient: 'from-orange-400 to-yellow-400' },
  { icon: CodeIcon, gradient: 'from-green-400 to-emerald-400' },
  { icon: BriefcaseIcon, gradient: 'from-blue-400 to-cyan-400' },
]

const features = [
  {
    icon: BookIcon,
    title: 'English Learning',
    desc: 'Master language skills',
    bgGradient: 'from-orange-50/50 to-orange-50',
    iconBg: 'bg-gradient-to-br from-orange-400 to-orange-500',
  },
  {
    icon: CodeIcon,
    title: 'Coding Practice',
    desc: 'Build tech expertise',
    bgGradient: 'from-green-50/50 to-green-50',
    iconBg: 'bg-gradient-to-br from-green-400 to-emerald-500',
  },
  {
    icon: BriefcaseIcon,
    title: 'Career Growth',
    desc: 'Professional development',
    bgGradient: 'from-blue-50/50 to-blue-50',
    iconBg: 'bg-gradient-to-br from-blue-400 to-cyan-500',
  },
]

const handlePreviewSuccess = (data: {
  displayName: string
  avatar: string
}) => {
  showAvatar.value = true
  displayName.value = data.displayName
  avatarUrl.value =
    data.avatar ||
    'https://images.unsplash.com/photo-1704726135027-9c6f034cfa41?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx1c2VyJTIwYXZhdGFyJTIwcG9ydHJhaXR8ZW58MXx8fHwxNzY1NDcxMDYzfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral'
}

const handlePreviewClear = () => {
  showAvatar.value = false
  displayName.value = ''
  avatarUrl.value = ''
}
</script>

<style scoped>
/* Vue Transitions - 与Figma源代码一致 */
.fade-in {
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.slide-in-left {
  animation: slideInLeft 0.6s ease-out;
}

@keyframes slideInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.slide-in-right {
  animation: slideInRight 0.4s ease-out;
}

@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.scale-in {
  animation: scaleIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes scaleIn {
  from {
    transform: scale(0);
  }
  to {
    transform: scale(1);
  }
}

.delay-200 {
  animation-delay: 0.2s;
}
.delay-300 {
  animation-delay: 0.3s;
}
.delay-400 {
  animation-delay: 0.4s;
}

/* Orbit动画已移到全局CSS (auth-common.css) */

/* Avatar transition */
.avatar-enter-active {
  transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.avatar-leave-active {
  transition: all 0.3s ease-out;
}

.avatar-enter-from,
.avatar-leave-to {
  opacity: 0;
  transform: scale(0.5);
}
</style>
