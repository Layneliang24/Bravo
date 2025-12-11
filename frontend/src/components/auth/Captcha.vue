<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="captcha-container" :aria-busy="loading">
    <div v-if="loading" class="loading" aria-label="加载中">
      <span>加载中...</span>
    </div>
    <div v-else-if="error" class="error" role="alert">
      <span>{{ error }}</span>
      <button type="button" @click="handleRetry" :disabled="disabled">
        重试
      </button>
    </div>
    <div v-else class="captcha-content">
      <div class="captcha-image-wrapper">
        <img
          v-if="captchaImage"
          :src="captchaImage"
          alt="验证码"
          class="captcha-image"
        />
        <div v-else class="captcha-placeholder">验证码加载中...</div>
      </div>
      <div class="captcha-input-wrapper">
        <input
          v-model="captchaAnswer"
          type="text"
          placeholder="请输入验证码"
          :disabled="disabled"
          class="captcha-input"
          @input="handleInput"
        />
        <button
          type="button"
          @click="refreshCaptcha"
          :disabled="disabled || loading"
          class="refresh-button"
          aria-label="刷新验证码"
        >
          🔄
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { ref, onMounted, defineExpose } from 'vue'

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
const captchaAnswer = ref('')

// API基础URL（可以根据环境配置调整）
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// 防抖定时器
let refreshTimer: ReturnType<typeof setTimeout> | null = null

const loadCaptcha = async (isRefresh = false) => {
  // 防止重复加载
  if (loading.value) {
    return
  }

  loading.value = true
  error.value = null

  try {
    const url = isRefresh
      ? `${API_BASE_URL}/api/auth/captcha/refresh/`
      : `${API_BASE_URL}/api/auth/captcha/`

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      const errorText = await response.text().catch(() => '')
      throw new Error(
        `获取验证码失败: ${response.status}${errorText ? ` - ${errorText}` : ''}`
      )
    }

    const data = await response.json()

    // 验证响应数据
    if (!data.captcha_id || !data.captcha_image) {
      throw new Error('验证码数据格式错误')
    }

    captchaId.value = data.captcha_id
    captchaImage.value = data.captcha_image

    // 重置答案
    captchaAnswer.value = ''

    // 发出事件
    emit('captcha-update', {
      captcha_id: captchaId.value,
      captcha_answer: captchaAnswer.value,
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : '获取验证码失败'
    console.error('Captcha load error:', err)
  } finally {
    loading.value = false
  }
}

const refreshCaptcha = () => {
  // 如果正在加载，直接返回
  if (loading.value) {
    return
  }

  // 防抖处理：避免频繁刷新（仅在非测试环境下启用）
  if (import.meta.env.MODE !== 'test') {
    if (refreshTimer) {
      clearTimeout(refreshTimer)
    }

    refreshTimer = setTimeout(() => {
      loadCaptcha(true)
      refreshTimer = null
    }, 300) // 300ms防抖延迟
  } else {
    // 测试环境下立即执行
    loadCaptcha(true)
  }
}

const handleInput = () => {
  emit('captcha-update', {
    captcha_id: captchaId.value,
    captcha_answer: captchaAnswer.value,
  })
}

const handleRetry = () => {
  loadCaptcha(false)
}

// 组件挂载时加载验证码
onMounted(() => {
  loadCaptcha()
})

// 暴露方法供父组件调用
defineExpose({
  refreshCaptcha,
})
</script>

<style scoped>
.captcha-container {
  width: 100%;
  margin-bottom: 1rem;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  font-family: 'Montserrat', sans-serif;
}

.error {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem;
  color: #ff6b6b;
  font-size: 14px;
  background: rgba(255, 100, 100, 0.15);
  border: 1px solid rgba(255, 100, 100, 0.4);
  border-radius: 7px;
  font-family: 'Montserrat', sans-serif;
}

.error span {
  color: #ff6b6b;
  font-weight: 400;
}

.error button {
  padding: 0.5rem 1rem;
  background-color: #ff6b6b;
  color: rgb(255, 255, 255);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 400;
  transition: all 0.3s ease;
}

.error button:hover:not(:disabled) {
  background-color: #ff5252;
  transform: translateY(-1px);
}

.error button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.captcha-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.captcha-image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 50px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 7px;
  background: rgba(40, 40, 40, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  overflow: hidden;
}

.captcha-image {
  width: auto;
  height: 100%;
  max-width: 100%;
  display: block;
  object-fit: contain;
}

.captcha-placeholder {
  padding: 1rem;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  font-family: 'Montserrat', sans-serif;
  text-align: center;
}

.captcha-input-wrapper {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.captcha-input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 7px;
  background: rgba(40, 40, 40, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: rgb(255, 255, 255);
  font-size: 15px;
  font-family: 'Montserrat', sans-serif;
  font-weight: 300;
  outline: none;
  transition: all 0.3s ease;
}

.captcha-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.captcha-input:focus {
  border-color: rgba(100, 150, 255, 0.5);
  background: rgba(50, 50, 50, 0.7);
  box-shadow: 0 0 0 2px rgba(100, 150, 255, 0.2);
}

.captcha-input:focus-visible {
  outline: none;
}

.captcha-input:disabled {
  background: rgba(40, 40, 40, 0.4);
  cursor: not-allowed;
  opacity: 0.6;
}

.refresh-button {
  padding: 0.75rem 1rem;
  background: rgba(40, 40, 40, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 7px;
  cursor: pointer;
  font-size: 1.25rem;
  color: rgb(255, 255, 255);
  transition: all 0.3s ease;
  min-width: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-button:hover:not(:disabled) {
  background: rgba(50, 50, 50, 0.7);
  border-color: rgba(100, 150, 255, 0.4);
}

.refresh-button:active:not(:disabled) {
  transform: scale(0.95);
}

.refresh-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}
</style>
