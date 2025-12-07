<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="captcha-container" :aria-busy="loading">
    <div v-if="loading" class="loading" aria-label="加载中">
      <span>加载中...</span>
    </div>
    <div v-else-if="error" class="error" role="alert">
      <span>{{ error }}</span>
      <button type="button" @click="loadCaptcha" :disabled="disabled">
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
import { ref, onMounted } from 'vue'

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

const loadCaptcha = async (isRefresh = false) => {
  loading.value = true
  error.value = null

  try {
    const url = isRefresh
      ? `${API_BASE_URL}/api/auth/captcha/refresh/`
      : `${API_BASE_URL}/api/auth/captcha/`

    const response = await fetch(url)

    if (!response.ok) {
      throw new Error(`获取验证码失败: ${response.status}`)
    }

    const data = await response.json()
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
  loadCaptcha(true)
}

const handleInput = () => {
  emit('captcha-update', {
    captcha_id: captchaId.value,
    captcha_answer: captchaAnswer.value,
  })
}

// 组件挂载时加载验证码
onMounted(() => {
  loadCaptcha()
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
  color: #6b7280;
  font-size: 0.875rem;
}

.error {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  color: #ef4444;
  font-size: 0.875rem;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.375rem;
}

.error button {
  padding: 0.5rem 1rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  font-size: 0.875rem;
}

.error button:hover:not(:disabled) {
  background-color: #dc2626;
}

.error button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  min-height: 40px;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  background-color: #f9fafb;
  overflow: hidden;
}

.captcha-image {
  width: 100%;
  height: auto;
  display: block;
}

.captcha-placeholder {
  padding: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
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
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s ease;
}

.captcha-input:focus {
  border-color: #3b82f6;
  outline: 2px solid transparent;
  outline-offset: 2px;
}

.captcha-input:focus-visible {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.captcha-input:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
  opacity: 0.6;
}

.refresh-button {
  padding: 0.75rem 1rem;
  background-color: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 1.25rem;
  transition: all 0.2s ease;
  min-width: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.refresh-button:hover:not(:disabled) {
  background-color: #e5e7eb;
  border-color: #9ca3af;
}

.refresh-button:active:not(:disabled) {
  transform: scale(0.95);
}

.refresh-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
