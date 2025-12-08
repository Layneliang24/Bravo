<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <form @submit.prevent="handleSubmit" class="register-form">
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
      required
    />
    <PasswordStrength :password="formData.password" />
    <FloatingInput
      v-model="formData.password_confirm"
      label="确认密码"
      type="password"
      :error="errors.password_confirm"
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
      {{ isSubmitting ? '注册中...' : '注册' }}
    </button>
  </form>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import FloatingInput from './FloatingInput.vue'
import Captcha from './Captcha.vue'
import PasswordStrength from './PasswordStrength.vue'

interface FormData {
  email: string
  password: string
  password_confirm: string
  captcha_id: string
  captcha_answer: string
}

const formData = reactive<FormData>({
  email: '',
  password: '',
  password_confirm: '',
  captcha_id: '',
  captcha_answer: '',
})

const errors = reactive<Partial<Record<keyof FormData, string>>>({})
const isSubmitting = ref(false)
const captchaRef = ref<InstanceType<typeof Captcha> | null>(null)
const router = useRouter()
const authStore = useAuthStore()

const handleCaptchaUpdate = (data: {
  captcha_id: string
  captcha_answer: string
}) => {
  formData.captcha_id = data.captcha_id
  formData.captcha_answer = data.captcha_answer
  errors.captcha_answer = ''
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

// 验证确认密码
const validatePasswordConfirm = (
  password: string,
  passwordConfirm: string
): string => {
  if (!passwordConfirm) {
    return '请确认密码'
  }
  if (password !== passwordConfirm) {
    return '两次输入的密码不一致'
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
  errors.password_confirm = ''
  errors.captcha_answer = ''
}

// 执行表单验证
const validateForm = (): boolean => {
  clearErrors()

  const emailError = validateEmail(formData.email)
  const passwordError = validatePassword(formData.password)
  const passwordConfirmError = validatePasswordConfirm(
    formData.password,
    formData.password_confirm
  )
  const captchaError = validateCaptcha(
    formData.captcha_id,
    formData.captcha_answer
  )

  if (emailError) errors.email = emailError
  if (passwordError) errors.password = passwordError
  if (passwordConfirmError) errors.password_confirm = passwordConfirmError
  if (captchaError) errors.captcha_answer = captchaError

  return !emailError && !passwordError && !passwordConfirmError && !captchaError
}

// 刷新验证码
const refreshCaptcha = async () => {
  if (captchaRef.value && typeof captchaRef.value.refreshCaptcha === 'function') {
    await captchaRef.value.refreshCaptcha()
  }
}

// 处理注册成功
const handleRegisterSuccess = async () => {
  await router.push('/')
}

// 处理注册失败
const handleRegisterError = async (error: any) => {
  const errorMessage = error?.message || '注册失败，请稍后重试'
  errors.captcha_answer = errorMessage
  await refreshCaptcha()
}

const handleSubmit = async () => {
  // 验证表单
  if (!validateForm()) {
    return
  }

  isSubmitting.value = true
  try {
    await authStore.register({
      email: formData.email,
      password: formData.password,
      password_confirm: formData.password_confirm,
      captcha_id: formData.captcha_id,
      captcha_answer: formData.captcha_answer,
    })

    await handleRegisterSuccess()
  } catch (error: any) {
    await handleRegisterError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.register-form {
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

.error-message {
  color: #ef4444;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}
</style>
