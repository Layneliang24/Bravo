<!-- REQ-ID: REQ-2025-003-user-login -->
<!-- 使用Figma源代码样式，包含字符波动动画 -->
<template>
  <div class="captcha-container">
    <div
      @click="refreshCaptcha"
      class="relative flex-shrink-0 overflow-hidden shadow-lg border-2 border-orange-200 cursor-pointer hover:scale-105 active:scale-95 transition-transform"
      style="
        background: linear-gradient(
          135deg,
          rgba(255, 237, 213, 1),
          rgba(254, 243, 199, 1)
        );
        width: 160px;
        height: 64px;
        border-radius: 14px;
      "
    >
      <!-- 装饰网格 -->
      <div class="absolute inset-0 opacity-10">
        <svg width="100%" height="100%">
          <defs>
            <pattern
              id="captchaGrid"
              width="10"
              height="10"
              patternUnits="userSpaceOnUse"
            >
              <path
                d="M 10 0 L 0 0 0 10"
                fill="none"
                stroke="rgba(249, 115, 22, 0.5)"
                stroke-width="0.5"
              />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#captchaGrid)" />
        </svg>
      </div>

      <!-- 验证码图片或文字 -->
      <div class="relative h-full flex items-center justify-center">
        <transition name="captcha" mode="out-in">
          <!-- 如果有图片，显示图片 -->
          <img
            v-if="captchaImage"
            :key="captchaId"
            :src="captchaImage"
            alt="验证码"
            class="w-full h-full object-contain"
            style="max-width: 100%; max-height: 100%"
          />
          <!-- 加载失败时显示错误提示和重试按钮 -->
          <div
            v-else-if="error"
            class="flex flex-col items-center justify-center gap-2 p-2"
          >
            <div class="text-red-500 text-xs text-center">{{ error }}</div>
            <button
              @click.stop="handleRetry"
              class="px-3 py-1 text-xs bg-orange-500 text-white rounded hover:bg-orange-600"
            >
              重试
            </button>
          </div>
          <!-- 加载中显示占位符 -->
          <div v-else class="text-gray-400 text-sm">加载中...</div>
        </transition>
      </div>

      <!-- 刷新图标（装饰性，点击整个区域刷新） -->
      <div
        class="absolute bottom-2 right-2 p-1 bg-white/80 rounded-lg pointer-events-none"
      >
        <svg
          class="w-4 h-4 text-orange-500 animate-spin-slow"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
      </div>
    </div>
    <input
      ref="captchaInputRef"
      :value="captchaAnswer"
      type="text"
      maxlength="4"
      placeholder="CODE"
      class="captcha-input"
      :disabled="disabled || loading"
      @input="handleInput"
      @blur="handleBlur"
    />
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { nextTick, onMounted, ref, watch } from 'vue'

interface Props {
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  disabled: false,
})

const emit = defineEmits<{
  'captcha-update': [
    data: {
      captcha_id: string
      captcha_answer: string
    },
  ]
}>()

const loading = ref(false)
const error = ref<string | null>(null)
const captchaId = ref('')
const captchaImage = ref('')
const captchaText = ref('') // 用于显示的验证码文本
const captchaAnswer = ref('') // 用户输入的验证码答案
const captchaInputRef = ref<HTMLInputElement | null>(null) // 输入框引用

// API基础URL - 使用相对路径，通过Vite proxy代理
// 注意：在浏览器环境中，必须使用相对路径，让Vite proxy处理
// 如果使用绝对路径（如http://backend:8000），浏览器无法解析Docker容器名
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// 判断是否在浏览器环境（Vite proxy可用）
// 如果API_BASE_URL是Docker容器名（如http://backend:8000），在浏览器中无法解析
// 应该使用相对路径，让Vite proxy处理
const useRelativePath =
  typeof window !== 'undefined' &&
  (!API_BASE_URL ||
    API_BASE_URL.includes('backend:') ||
    API_BASE_URL.includes('localhost') ||
    API_BASE_URL.includes('127.0.0.1'))

// 不再使用文本降级方案，验证码必须是图片

const loadCaptcha = async (isRefresh = false) => {
  if (props.disabled || loading.value) return

  loading.value = true
  error.value = null

  try {
    // 如果是刷新，使用刷新API（会删除旧的验证码）
    // 如果是首次加载，使用获取API
    // 在浏览器环境中，使用相对路径让Vite proxy处理
    // 在服务器端渲染（SSR）或测试环境中，使用绝对路径
    const url = useRelativePath
      ? isRefresh
        ? '/api/auth/captcha/refresh/'
        : '/api/auth/captcha/'
      : isRefresh
        ? `${API_BASE_URL}/api/auth/captcha/refresh/`
        : `${API_BASE_URL}/api/auth/captcha/`
    const method = isRefresh ? 'POST' : 'GET'
    // 如果是刷新且没有captchaId，发送空对象；如果有captchaId，发送包含captcha_id的对象
    const body = isRefresh
      ? JSON.stringify(
          captchaId.value ? { captcha_id: captchaId.value } : {}
        )
      : undefined

    // 构建请求头：POST请求需要Content-Type，GET请求不需要
    const headers: Record<string, string> = {}
    if (method === 'POST') {
      headers['Content-Type'] = 'application/json'
    }

    const response = await fetch(url, {
      method,
      headers,
      body,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    // 验证响应数据
    if (!data.captcha_id) {
      throw new Error('验证码ID缺失')
    }

    if (!data.captcha_image || !data.captcha_image.startsWith('data:image')) {
      throw new Error(
        `验证码图片格式错误: ${data.captcha_image?.substring(0, 50) || 'empty'}`
      )
    }

    captchaId.value = data.captcha_id
    captchaImage.value = data.captcha_image
    captchaText.value = '' // 清除文本，只显示图片

    // 触发更新事件（只传递captcha_id，不传递答案）
    emit('captcha-update', {
      captcha_id: captchaId.value,
      captcha_answer: '', // 不自动填充，让用户手动输入
    })
  } catch (err) {
    // 处理不同类型的错误
    if (err instanceof TypeError && err.message.includes('fetch')) {
      // 网络错误（Failed to fetch）
      error.value = 'Failed to fetch'
    } else if (err instanceof Error) {
      error.value = err.message
    } else {
      error.value = '验证码加载失败'
    }
    // 错误已通过error.value显示给用户，不需要控制台输出
    // 验证码必须显示图片，不显示降级文本
    captchaImage.value = ''
    captchaText.value = ''
  } finally {
    loading.value = false
  }
}

const refreshCaptcha = async () => {
  if (props.disabled || loading.value) return
  await loadCaptcha(true)
}

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  // 获取输入值并转换为大写
  let value = target.value.toUpperCase()
  // 限制长度为4位
  if (value.length > 4) {
    value = value.substring(0, 4)
  }
  // 更新本地值
  captchaAnswer.value = value
  // 触发更新事件（实时更新，不仅是4位时）
  // 重要：只在输入时触发，不在这里触发blur事件
  emitUpdate()
}

const handleBlur = () => {
  // 重要：失焦时也触发更新，但父组件应该检查是否真的需要验证
  // 如果验证码已经是4位且刚刚验证过，不应该再次验证
  emitUpdate()
}

const emitUpdate = () => {
  emit('captcha-update', {
    captcha_id: captchaId.value,
    captcha_answer: captchaAnswer.value,
  })
}

const handleRetry = () => {
  refreshCaptcha()
}

// 当刷新验证码时清空输入
watch(captchaId, (newId, oldId) => {
  // 只有当验证码ID真正改变时才清空输入
  if (newId !== oldId) {
    captchaAnswer.value = ''
    emitUpdate()
  }
})

// 暴露方法供父组件调用
defineExpose({
  refreshCaptcha,
})

onMounted(() => {
  // 加载真实的验证码（包含图片）
  loadCaptcha()

  // 在下一个tick中添加事件监听器，确保DOM已完全渲染
  nextTick(() => {
    if (captchaInputRef.value) {
      // 输入事件监听器已添加
      captchaInputRef.value.addEventListener('input', handleInput)
      captchaInputRef.value.addEventListener('blur', handleBlur)
    }
  })
})
</script>

<style scoped>
/* 字符波动动画 - 与Figma源代码一致 */
@keyframes char-wave {
  0%,
  100% {
    transform: translateY(0) rotate(var(--char-rotate, 0deg));
  }
  50% {
    transform: translateY(-4px) rotate(var(--char-rotate, 0deg));
  }
}

.animate-char-wave {
  animation: char-wave 2s ease-in-out infinite;
}

/* Captcha transition - 与Figma源代码一致 */
.captcha-enter-active,
.captcha-leave-active {
  transition: all 0.3s ease;
}

.captcha-enter-from {
  opacity: 0;
  transform: scale(0.8) rotate(-5deg);
}

.captcha-leave-to {
  opacity: 0;
  transform: scale(1.2) rotate(5deg);
}

/* 验证码容器样式 */
.captcha-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

/* 验证码输入框样式 - 符合Figma设计规范 */
.captcha-input {
  flex: 1;
  height: 64px;
  border: 2px solid rgba(249, 115, 22, 0.15);
  border-radius: 14px;
  padding: 0 1rem;
  font-size: 16px;
  font-weight: 500;
  color: #1f2937;
  background-color: white;
  transition: all 0.2s ease;
  text-transform: uppercase;
}

.captcha-input:focus {
  outline: none;
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
}

.captcha-input::placeholder {
  color: #9ca3af;
}

.captcha-input:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background-color: #f9fafb;
}
</style>
