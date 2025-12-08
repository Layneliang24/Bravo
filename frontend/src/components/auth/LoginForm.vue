<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <UserPreview
    v-if="previewVisible"
    :display-name="previewUser?.display_name || ''"
    :avatar-url="previewUser?.avatar_url || null"
    :avatar-letter="previewUser?.avatar_letter || ''"
    :loading="previewLoading"
  />
  <form @submit.prevent="handleSubmit" class="login-form">
    <FloatingInput
      v-model="formData.email"
      label="邮箱"
      type="email"
      :error="errors.email"
      required
    />
    <FloatingInput
      v-model="formData.password"
      label="密码"
      type="password"
      :error="errors.password"
      @blur="handlePasswordBlur"
      required
    />
    <div v-if="errors.captcha_answer" class="error-message">
      {{ errors.captcha_answer }}
    </div>
    <Captcha
      ref="captchaRef"
      :disabled="isSubmitting"
      @captcha-update="handleCaptchaUpdate"
    />
    <button type="submit" :disabled="isSubmitting" class="submit-button">
      {{ isSubmitting ? '登录中...' : '登录' }}
    </button>
  </form>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import FloatingInput from './FloatingInput.vue'
import Captcha from './Captcha.vue'
import UserPreview from './UserPreview.vue'

// 防抖函数
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: ReturnType<typeof setTimeout> | null = null
  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }
    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}

interface FormData {
  email: string
  password: string
  captcha_id: string
  captcha_answer: string
}

const formData = reactive<FormData>({
  email: '',
  password: '',
  captcha_id: '',
  captcha_answer: '',
})

const errors = reactive<Partial<Record<keyof FormData, string>>>({})
const isSubmitting = ref(false)
const previewLoading = ref(false)
const captchaRef = ref<InstanceType<typeof Captcha> | null>(null)
const router = useRouter()
const authStore = useAuthStore()
const previewUser = computed(() => authStore.preview?.user || null)
const previewVisible = computed(
  () => previewLoading.value || !!previewUser.value
)

const handleCaptchaUpdate = (data: {
  captcha_id: string
  captcha_answer: string
}) => {
  formData.captcha_id = data.captcha_id
  formData.captcha_answer = data.captcha_answer
  errors.captcha_answer = ''
  triggerPreview()
}

// 邮箱格式验证正则
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

// 验证邮箱格式
const validateEmail = (email: string): string => {
  if (!email) {
    return '请输入邮箱'
  }
  if (!EMAIL_REGEX.test(email)) {
    return '邮箱格式不正确'
  }
  return ''
}

// 验证密码
const validatePassword = (password: string): string => {
  if (!password) {
    return '请输入密码'
  }
  if (password.length < 8) {
    return '密码长度至少为8位'
  }
  return ''
}

// 验证验证码
const validateCaptcha = (captchaId: string, captchaAnswer: string): string => {
  if (!captchaId || !captchaAnswer) {
    return '请输入验证码'
  }
  return ''
}

// 清除所有错误
const clearErrors = () => {
  errors.email = ''
  errors.password = ''
  errors.captcha_answer = ''
}

// 执行表单验证
const validateForm = (): boolean => {
  clearErrors()

  const emailError = validateEmail(formData.email)
  const passwordError = validatePassword(formData.password)
  const captchaError = validateCaptcha(
    formData.captcha_id,
    formData.captcha_answer
  )

  if (emailError) errors.email = emailError
  if (passwordError) errors.password = passwordError
  if (captchaError) errors.captcha_answer = captchaError

  return !emailError && !passwordError && !captchaError
}

// 刷新验证码
const refreshCaptcha = async () => {
  if (captchaRef.value && typeof captchaRef.value.refreshCaptcha === 'function') {
    await captchaRef.value.refreshCaptcha()
  }
}

// 处理登录成功
const handleLoginSuccess = async () => {
  await router.push('/')
}

// 处理登录失败
const handleLoginError = async (error: any) => {
  const errorMessage = error?.message || '登录失败，请稍后重试'
  errors.captcha_answer = errorMessage
  await refreshCaptcha()
}

const triggerPreview = async () => {
  // 验证必要字段
  if (
    !formData.email ||
    !formData.password ||
    !formData.captcha_id ||
    !formData.captcha_answer
  ) {
    return
  }

  // 验证邮箱格式
  if (!EMAIL_REGEX.test(formData.email)) {
    return
  }

  // 验证密码长度
  if (formData.password.length < 8) {
    return
  }

  previewLoading.value = true
  try {
    await authStore.previewLogin({
      email: formData.email,
      password: formData.password,
      captcha_id: formData.captcha_id,
      captcha_answer: formData.captcha_answer,
    })
  } catch (error) {
    // 静默处理错误，不影响用户体验
    console.error('Preview login failed:', error)
  } finally {
    previewLoading.value = false
  }
}

// 使用防抖优化，避免频繁调用
const debouncedTriggerPreview = debounce(triggerPreview, 500)

const handlePasswordBlur = () => {
  debouncedTriggerPreview()
}

const handleSubmit = async () => {
  // 验证表单
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true
  try {
    await authStore.login({
      email: formData.email,
      password: formData.password,
      captcha_id: formData.captcha_id,
      captcha_answer: formData.captcha_answer,
    })

    await handleLoginSuccess()
  } catch (error: any) {
    await handleLoginError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.login-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

.submit-button {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.submit-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.submit-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
}
</style>
