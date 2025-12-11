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
    <!-- Username 输入框 -->
    <div class="username-input">
      <label class="username-label">Username</label>
      <input
        v-model="formData.email"
        type="text"
        placeholder="Enter your username"
        class="input-field"
        :class="{ 'has-error': errors.email }"
        required
      />
      <div v-if="errors.email" class="error-message">{{ errors.email }}</div>
    </div>

    <!-- Password 输入框 -->
    <div class="password-input">
      <label class="password-label">Password</label>
      <input
        v-model="formData.password"
        type="password"
        placeholder="Enter your password"
        class="input-field"
        :class="{ 'has-error': errors.password }"
        @blur="handlePasswordBlur"
        required
      />
      <div v-if="errors.password" class="error-message">{{ errors.password }}</div>
    </div>

    <!-- Forgot Password 链接 -->
    <div class="forgot-password-wrapper">
      <a href="#" class="forgot-password">Forgot Password?</a>
    </div>

    <!-- 验证码 -->
    <div v-if="errors.captcha_answer" class="error-message">
      {{ errors.captcha_answer }}
    </div>
    <Captcha
      ref="captchaRef"
      :disabled="isSubmitting"
      @captcha-update="handleCaptchaUpdate"
    />

    <!-- 登录按钮 -->
    <button type="submit" :disabled="isSubmitting" class="login-button">
      {{ isSubmitting ? '登录中...' : 'LOGIN' }}
    </button>

    <!-- Register 文本 -->
    <p class="register-text">New to Logo? Register Here</p>
  </form>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { debounce } from '@/utils/debounce'
import {
  EMAIL_REGEX,
  validateEmail,
  validatePassword,
  validateCaptcha,
} from '@/utils/validation'
import FloatingInput from './FloatingInput.vue'
import Captcha from './Captcha.vue'
import UserPreview from './UserPreview.vue'

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
/* Glassmorphism 设计 - 根据 Figma 设计规范 */
.login-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  font-family: 'Montserrat', sans-serif;
}

/* 输入框容器 */
.username-input,
.password-input {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 0;
}

/* 标签样式 - 15px, Montserrat Regular, 白色 */
.username-label,
.password-label {
  font-family: 'Montserrat', sans-serif;
  font-size: 15px;
  font-weight: 400;
  line-height: 18.28px;
  color: rgb(255, 255, 255);
  text-align: left;
}

/* 输入框样式 - 419x50px, 圆角 7px，深色背景 */
.input-field {
  width: 100%;
  height: 50px;
  padding: 0 1rem;
  background: rgba(40, 40, 40, 0.6);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 7px;
  color: rgb(255, 255, 255);
  font-family: 'Montserrat', sans-serif;
  font-size: 15px;
  font-weight: 300;
  line-height: 18.28px;
  outline: none;
  transition: all 0.3s ease;
}

.input-field::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.input-field:focus {
  border-color: rgba(100, 150, 255, 0.5);
  background: rgba(50, 50, 50, 0.7);
  box-shadow: 0 0 0 2px rgba(100, 150, 255, 0.2);
}

.input-field.has-error {
  border-color: rgba(255, 80, 80, 0.6);
  background: rgba(60, 40, 40, 0.6);
}

/* Forgot Password 链接 */
.forgot-password-wrapper {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  margin-top: -0.5rem;
  margin-bottom: 0.5rem;
}

.forgot-password {
  font-family: 'Montserrat', sans-serif;
  font-size: 12px;
  font-weight: 400;
  line-height: 14.63px;
  color: rgb(255, 255, 255);
  text-decoration: none;
  transition: opacity 0.3s ease;
}

.forgot-password:hover {
  opacity: 0.8;
}

/* 登录按钮 - 419x50px, 背景色 rgb(165, 217, 208), 圆角 7px */
.login-button {
  width: 100%;
  height: 50px;
  background: rgb(165, 217, 208);
  border: none;
  border-radius: 7px;
  color: rgb(0, 0, 0);
  font-family: 'Montserrat', sans-serif;
  font-size: 15px;
  font-weight: 600;
  line-height: 18.28px;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 1rem;
  margin-bottom: 0;
}

.login-button:hover:not(:disabled) {
  background: rgb(145, 197, 188);
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  background: rgba(165, 217, 208, 0.5);
  cursor: not-allowed;
  transform: none;
}

/* Register 文本 - 15px, Montserrat Light, 白色 */
.register-text {
  font-family: 'Montserrat', sans-serif;
  font-size: 15px;
  font-weight: 300;
  line-height: 18.28px;
  color: rgb(255, 255, 255);
  text-align: center;
  margin-top: 1rem;
  margin-bottom: 0;
}

/* 错误消息 - 红色文本 */
.error-message {
  color: #ff6b6b;
  font-size: 14px;
  margin-top: 0.5rem;
  font-family: 'Montserrat', sans-serif;
  font-weight: 400;
}

/* 验证码错误框 - 红色背景框样式 */
:deep(.captcha-container .error) {
  background: rgba(255, 100, 100, 0.2);
  border: 1px solid rgba(255, 100, 100, 0.5);
  border-radius: 7px;
  padding: 1rem;
  margin-top: 1rem;
}

:deep(.captcha-container .error span) {
  color: #ff6b6b;
  font-size: 14px;
}

:deep(.captcha-container .error button) {
  background: #ff6b6b;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.5rem 1rem;
  margin-top: 0.5rem;
  cursor: pointer;
  font-family: 'Montserrat', sans-serif;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-form {
    gap: 1.25rem;
  }

  .input-field,
  .login-button {
    height: 45px;
  }

  .username-label,
  .password-label {
    font-size: 14px;
  }

  .forgot-password {
    font-size: 11px;
  }

  .register-text {
    font-size: 14px;
  }
}
</style>
