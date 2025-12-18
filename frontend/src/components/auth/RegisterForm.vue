<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <!-- 注册成功后的邮箱验证提示界面 -->
  <div v-if="isRegistered" class="email-verification-prompt register-success">
    <div class="verification-icon">📧</div>
    <h2 class="verification-title">注册成功！</h2>
    <p
      class="verification-message success-message"
      data-testid="success-message"
    >
      我们已向您的邮箱 <strong>{{ registeredEmail }}</strong> 发送了验证邮件。
    </p>
    <p class="verification-instruction">
      请查收您的邮箱（包括垃圾邮件文件夹），点击验证链接以完成邮箱验证。验证链接将在24小时内有效。
    </p>
    <div
      v-if="verificationMessage"
      :class="['verification-feedback', verificationMessageType]"
    >
      {{ verificationMessage }}
    </div>
    <div class="verification-actions">
      <button
        type="button"
        @click="handleResendVerification"
        :disabled="isResending"
        class="resend-button"
      >
        {{ isResending ? '发送中...' : '重新发送验证邮件' }}
      </button>
      <button type="button" @click="handleGoToHome" class="home-button">
        返回首页
      </button>
    </div>
  </div>

  <!-- 注册表单 -->
  <form v-else @submit.prevent="handleSubmit" class="register-form">
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
    <!-- 验证码区域 - Captcha组件已包含输入框，不需要重复 -->
    <div class="flex items-center gap-4 mt-4" style="min-height: 64px">
      <Captcha
        ref="captchaRef"
        :disabled="isSubmitting"
        @captcha-update="handleCaptchaUpdate"
      />
    </div>
    <div v-if="errors.captcha_answer" class="error-message mt-2">
      {{ errors.captcha_answer }}
    </div>
    <button
      type="submit"
      :disabled="isSubmitting || !isFormValid"
      class="w-full mt-6 py-4 bg-gradient-to-r from-orange-500 to-yellow-500 text-white rounded-xl font-semibold tracking-wide hover:from-orange-400 hover:to-yellow-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
    >
      {{ isSubmitting ? '注册中...' : '创建账户' }}
    </button>
  </form>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { useAuthStore } from '@/stores/auth'
import {
  EMAIL_REGEX,
  validateCaptcha,
  validateEmail,
  validatePassword,
  validatePasswordConfirm,
} from '@/utils/validation'
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import Captcha from './Captcha.vue'
import FloatingInput from './FloatingInput.vue'
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

// 表单验证状态
const isFormValid = computed(() => {
  return (
    formData.email &&
    EMAIL_REGEX.test(formData.email) &&
    formData.password &&
    formData.password.length >= 8 &&
    formData.password_confirm &&
    formData.password === formData.password_confirm &&
    formData.captcha_id &&
    formData.captcha_answer
  )
})

// 邮箱验证相关状态
const isRegistered = ref(false)
const registeredEmail = ref('')
const isResending = ref(false)
const verificationMessage = ref('')
const verificationMessageType = ref<'success' | 'error'>('success')

const handleCaptchaUpdate = (data: {
  captcha_id: string
  captcha_answer: string
}) => {
  // 更新captcha_id（刷新验证码时会触发）
  formData.captcha_id = data.captcha_id
  // 更新captcha_answer（Captcha组件内部输入框的值）
  formData.captcha_answer = data.captcha_answer || ''
  // 如果验证码刷新了，清空之前的错误
  if (!data.captcha_answer) {
    errors.captcha_answer = ''
  } else if (data.captcha_answer.length === 4) {
    // 如果输入了4位，自动验证
    const captchaError = validateCaptcha(
      formData.captcha_id,
      formData.captcha_answer
    )
    if (captchaError) {
      errors.captcha_answer = captchaError
    } else {
      errors.captcha_answer = ''
    }
  }
}

// 验证码是否有效
const isCaptchaValid = computed(() => {
  return (
    formData.captcha_answer &&
    formData.captcha_answer.length === 4 &&
    !errors.captcha_answer
  )
})

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
  if (
    captchaRef.value &&
    typeof captchaRef.value.refreshCaptcha === 'function'
  ) {
    await captchaRef.value.refreshCaptcha()
  }
}

// 处理注册成功
const handleRegisterSuccess = async (email: string) => {
  isRegistered.value = true
  registeredEmail.value = email
  // 不清空表单，保留邮箱信息用于重发验证邮件
}

// 处理注册失败
const handleRegisterError = async (error: any) => {
  const errorMessage = error?.message || '注册失败，请稍后重试'
  errors.captcha_answer = errorMessage
  // 如果是验证码错误，自动刷新验证码
  if (
    errorMessage.includes('验证码') ||
    errorMessage.includes('captcha') ||
    errorMessage.includes('验证码错误')
  ) {
    // 先清空验证码输入，避免用户继续使用错误的验证码
    formData.captcha_answer = ''
    // 然后刷新验证码
    await refreshCaptcha()
    // 确保captcha_id也更新了
    if (captchaRef.value) {
      // 等待一下确保刷新完成
      await new Promise(resolve => setTimeout(resolve, 100))
    }
  }
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

    await handleRegisterSuccess(formData.email)
  } catch (error: any) {
    await handleRegisterError(error)
  } finally {
    isSubmitting.value = false
  }
}

// 处理重新发送验证邮件
const handleResendVerification = async () => {
  if (!registeredEmail.value) {
    return
  }

  isResending.value = true
  verificationMessage.value = ''

  try {
    const response = await authStore.sendEmailVerification({
      email: registeredEmail.value,
    })

    if (response && response.message) {
      verificationMessage.value = response.message
      verificationMessageType.value = 'success'
    }
  } catch (error: any) {
    const errorMessage =
      error?.message ||
      '发送验证邮件失败，请稍后重试。如果问题持续存在，请联系客服支持。'
    verificationMessage.value = errorMessage
    verificationMessageType.value = 'error'
  } finally {
    isResending.value = false
  }
}

// 返回首页
const handleGoToHome = () => {
  router.push('/')
}
</script>

<style scoped>
.register-form {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  min-height: auto;
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

.error-message {
  color: var(--color-error);
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

/* 邮箱验证提示界面样式 */
.email-verification-prompt {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.verification-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.verification-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.verification-message {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

.verification-message strong {
  color: var(--color-primary-dark-blue);
  font-weight: 600;
}

.verification-instruction {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.verification-feedback {
  padding: 0.75rem 1rem;
  border-radius: var(--border-radius);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
  text-align: center;
}

.verification-feedback.success {
  color: #065f46;
  background-color: #d1fae5;
  border: 1px solid var(--color-success);
}

.verification-feedback.error {
  color: #991b1b;
  background-color: #fee2e2;
  border: 1px solid var(--color-error);
}

.verification-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.resend-button {
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

.resend-button:hover:not(:disabled) {
  background: var(--gradient-button-hover);
  box-shadow: var(--box-shadow-lg);
  transform: translateY(-1px);
}

.resend-button:disabled {
  background: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.home-button {
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid #d1d5db;
  border-radius: var(--border-radius);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.home-button:hover {
  background-color: #f9fafb;
  color: var(--text-primary);
  border-color: #9ca3af;
}
</style>
