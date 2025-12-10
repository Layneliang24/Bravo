<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <form @submit.prevent="handleSubmit" class="password-reset-form">
    <FloatingInput
      v-model="formData.email"
      label="邮箱"
      type="email"
      :error="errors.email"
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
    <div v-if="successMessage" class="success-message">
      {{ successMessage }}
    </div>
    <button type="submit" :disabled="isSubmitting" class="submit-button">
      {{ isSubmitting ? '发送中...' : '发送重置邮件' }}
    </button>
  </form>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { reactive, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { validateEmail, validateCaptcha } from '@/utils/validation'
import FloatingInput from './FloatingInput.vue'
import Captcha from './Captcha.vue'

interface FormData {
  email: string
  captcha_id: string
  captcha_answer: string
}

const formData = reactive<FormData>({
  email: '',
  captcha_id: '',
  captcha_answer: '',
})

const errors = reactive<Partial<Record<keyof FormData, string>>>({})
const isSubmitting = ref(false)
const successMessage = ref('')
const captchaRef = ref<InstanceType<typeof Captcha> | null>(null)
const authStore = useAuthStore()

const handleCaptchaUpdate = (data: {
  captcha_id: string
  captcha_answer: string
}) => {
  formData.captcha_id = data.captcha_id
  formData.captcha_answer = data.captcha_answer
  errors.captcha_answer = ''
}

const handleSubmit = async () => {
  // 清除之前的错误和成功消息
  errors.email = ''
  errors.captcha_answer = ''
  successMessage.value = ''

  // 验证邮箱
  const emailError = validateEmail(formData.email)
  if (emailError) {
    errors.email = emailError
    return
  }

  // 验证验证码
  const captchaError = validateCaptcha(
    formData.captcha_id,
    formData.captcha_answer
  )
  if (captchaError) {
    errors.captcha_answer = captchaError
    return
  }

  isSubmitting.value = true

  try {
    const response = await authStore.sendPasswordReset({
      email: formData.email,
      captcha_id: formData.captcha_id,
      captcha_answer: formData.captcha_answer,
    })

    if (response && response.message) {
      successMessage.value = response.message
      // 清空表单
      formData.email = ''
      formData.captcha_id = ''
      formData.captcha_answer = ''
      // 刷新验证码
      if (captchaRef.value && typeof captchaRef.value.refreshCaptcha === 'function') {
        await captchaRef.value.refreshCaptcha()
      }
    }
  } catch (error: any) {
    // 处理错误
    const errorMessage = error?.response?.data?.error || error?.message || '发送失败，请稍后重试'

    if (error?.response?.data?.code === 'INVALID_CAPTCHA') {
      errors.captcha_answer = '验证码错误'
      // 刷新验证码
      if (captchaRef.value && typeof captchaRef.value.refreshCaptcha === 'function') {
        await captchaRef.value.refreshCaptcha()
      }
    } else if (error?.response?.data?.code === 'INVALID_EMAIL') {
      errors.email = '邮箱格式不正确'
    } else {
      errors.captcha_answer = errorMessage
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.password-reset-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.error-message {
  color: var(--color-error);
  font-size: 0.875rem;
  margin-top: -0.5rem;
}

.success-message {
  color: var(--color-success);
  font-size: 0.875rem;
  padding: 0.75rem;
  background-color: #d1fae5;
  border-radius: var(--border-radius);
  text-align: center;
}

.submit-button {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--gradient-button);
  color: var(--text-light);
  border: none;
  border-radius: var(--border-radius);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--box-shadow);
}

.submit-button:hover:not(:disabled) {
  background: var(--gradient-button-hover);
  box-shadow: var(--box-shadow-lg);
  transform: translateY(-1px);
}

.submit-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}
</style>
