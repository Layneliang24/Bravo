<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
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
      required
    />
    <Captcha
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
import { reactive, ref } from 'vue'
import FloatingInput from './FloatingInput.vue'
import Captcha from './Captcha.vue'

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

const handleCaptchaUpdate = (data: {
  captcha_id: string
  captcha_answer: string
}) => {
  formData.captcha_id = data.captcha_id
  formData.captcha_answer = data.captcha_answer
  errors.captcha_answer = ''
}

const handleSubmit = async () => {
  // 清除之前的错误
  errors.email = ''
  errors.password = ''

  // 基础验证
  if (!formData.email) {
    errors.email = '请输入邮箱'
    return
  }

  if (!formData.password) {
    errors.password = '请输入密码'
    return
  }

  if (!formData.captcha_id || !formData.captcha_answer) {
    errors.captcha_answer = '请输入验证码'
    return
  }

  // TODO: 集成Auth Store登录功能
  isSubmitting.value = true
  try {
    // 登录逻辑将在后续任务中实现
    console.log('Login attempt:', formData)
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
