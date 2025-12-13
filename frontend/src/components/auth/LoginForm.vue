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
    <!-- USERNAME 输入框 -->
    <div class="input-group">
      <label class="input-label">USERNAME</label>
      <FloatingInput
        v-model="formData.email"
        label="USERNAME"
        type="text"
        placeholder="Enter your username"
        :error="errors.email"
        icon="👤"
        required
        @blur="validateEmail"
      />
    </div>

    <!-- PASSWORD 输入框 -->
    <div class="input-group">
      <label class="input-label">PASSWORD</label>
      <FloatingInput
        v-model="formData.password"
        label="PASSWORD"
        type="password"
        placeholder="Enter your password"
        :error="errors.password"
        icon="🔒"
        required
        @blur="handlePasswordBlur"
      />
    </div>

    <!-- SECURITY CODE 验证码 -->
    <div class="input-group">
      <label class="input-label">SECURITY CODE</label>
      <div v-if="errors.captcha_answer" class="error-message">
        {{ errors.captcha_answer }}
      </div>
      <Captcha
        ref="captchaRef"
        :disabled="isSubmitting"
        @captcha-update="handleCaptchaUpdate"
      />
    </div>

    <!-- 登录按钮 -->
    <button type="submit" :disabled="isSubmitting" class="login-button">
      {{ isSubmitting ? '登录中...' : 'LOGIN' }}
    </button>

    <!-- Register 链接 -->
    <p class="register-text">
      Don't have an account?
      <router-link to="/register" class="register-link">Sign up now →</router-link>
    </p>
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
import { useRouter } from 'vue-router'

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

// 验证邮箱格式
const validateEmail = () => {
  if (formData.email && !EMAIL_REGEX.test(formData.email)) {
    errors.email = 'Please enter a valid email address'
  } else {
    errors.email = ''
  }
}
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
/* Figma设计规范 - 登录表单 */
.login-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-input-gap);
  font-family: var(--font-family);
}

/* 输入框组 */
.input-group {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-label-input);
}

/* 标签样式 - 14px, Arial Bold */
.input-label {
  font-family: var(--font-family);
  font-size: var(--font-size-label);
  font-weight: bold;
  line-height: var(--line-height-label);
  letter-spacing: 0.35px;
  color: var(--text-label);
  text-align: left;
  height: 20px;
}

/* 登录按钮 */
.login-button {
  width: 100%;
  height: var(--input-height);
  background: linear-gradient(
    135deg,
    var(--color-orange-gradient-start) 0%,
    var(--color-orange-gradient-end) 100%
  );
  border: none;
  border-radius: var(--input-border-radius);
  color: white;
  font-family: var(--font-family);
  font-size: var(--font-size-label);
  font-weight: bold;
  line-height: var(--line-height-label);
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 8px;
  box-shadow: var(--shadow-input);
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0px 6px 16px 0px rgba(249, 115, 22, 0.2);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Register 文本 */
.register-text {
  font-family: var(--font-family);
  font-size: var(--font-size-label);
  font-weight: 400;
  line-height: var(--line-height-label);
  color: var(--text-secondary);
  text-align: center;
  margin-top: 16px;
  margin-bottom: 0;
}

.register-link {
  color: var(--text-link);
  font-weight: bold;
  text-decoration: none;
  transition: opacity 0.2s ease;
}

.register-link:hover {
  opacity: 0.8;
}

/* 错误消息 */
.error-message {
  color: var(--color-error);
  font-size: 14px;
  margin-top: 4px;
  font-family: var(--font-family);
  font-weight: 400;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-form {
    gap: 1.5rem;
  }

  .input-label {
    font-size: 13px;
  }

  .login-button {
    height: 56px;
  }

  .register-text {
    font-size: 13px;
  }
}
</style>
