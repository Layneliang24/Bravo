<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <form @submit.prevent="handleSubmit" class="login-form space-y-6">
    <!-- EMAIL 输入框 - 使用Figma源代码样式 -->
    <div>
      <label
        class="block text-gray-700 mb-3 text-sm font-semibold tracking-wide"
        >EMAIL</label
      >
      <div class="relative group">
        <div
          class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-orange-500 transition-colors"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
            />
          </svg>
        </div>
        <input
          v-model="formData.email"
          type="text"
          autocomplete="username"
          class="w-full bg-white border-2 pl-12 pr-4 text-gray-800 placeholder:text-gray-400 focus:outline-none focus:bg-orange-50/30 transition-all"
          style="
            border-color: rgba(249, 115, 22, 0.15);
            border-radius: 14px;
            height: 60px;
          "
          placeholder="Enter your email"
          @blur="validateEmailLocal"
          @input="handleEmailInput"
        />
        <transition name="check">
          <div
            v-if="isEmailValid"
            class="absolute right-4 top-1/2 -translate-y-1/2"
          >
            <svg
              class="w-6 h-6 text-green-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </transition>
        <div
          v-if="formData.email"
          class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-400 via-yellow-400 to-green-400 rounded-b-xl"
        />
      </div>
      <div v-if="errors.email" class="mt-2 text-red-500 text-sm">
        {{ errors.email }}
      </div>
    </div>

    <!-- PASSWORD 输入框 - 使用Figma源代码样式 -->
    <div>
      <label
        class="block text-gray-700 mb-3 text-sm font-semibold tracking-wide"
        >PASSWORD</label
      >
      <div class="relative group">
        <div
          class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within:text-orange-500 transition-colors"
        >
          <svg
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            />
          </svg>
        </div>
        <input
          v-model="formData.password"
          :type="showPassword ? 'text' : 'password'"
          autocomplete="current-password"
          class="w-full bg-white border-2 pl-12 pr-12 text-gray-800 placeholder:text-gray-400 focus:outline-none focus:bg-orange-50/30 transition-all"
          style="
            border-color: rgba(249, 115, 22, 0.15);
            border-radius: 14px;
            height: 60px;
          "
          placeholder="Enter your password"
          @blur="handlePasswordBlur"
          @input="handlePasswordInput"
        />
        <button
          type="button"
          @click="showPassword = !showPassword"
          class="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
        >
          <svg
            v-if="showPassword"
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"
            />
          </svg>
          <svg
            v-else
            class="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
            />
          </svg>
        </button>
        <transition name="check">
          <div
            v-if="isPasswordValid"
            class="absolute right-12 top-1/2 -translate-y-1/2"
          >
            <svg
              class="w-6 h-6 text-green-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
        </transition>
        <div
          v-if="formData.password"
          class="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-orange-400 via-yellow-400 to-green-400 rounded-b-xl"
        />
      </div>
      <div v-if="errors.password" class="mt-2 text-red-500 text-sm">
        {{ errors.password }}
      </div>
    </div>

    <!-- SECURITY CODE 验证码 - 使用Figma源代码样式 -->
    <div>
      <label
        class="block text-gray-700 mb-3 text-sm font-semibold tracking-wide"
        >SECURITY CODE</label
      >
      <div class="flex gap-4">
        <!-- 验证码显示区和输入框 -->
        <Captcha
          ref="captchaRef"
          :disabled="isSubmitting"
          @captcha-update="handleCaptchaUpdate"
        />
      </div>
      <div
        v-if="errors.captcha_answer"
        class="mt-2 text-red-500 text-sm"
        data-testid="captcha-error-message"
      >
        {{ errors.captcha_answer }}
      </div>
    </div>

    <!-- 登录按钮 -->
    <button
      type="submit"
      :disabled="buttonDisabled"
      class="w-full mt-6 py-4 bg-gradient-to-r from-orange-500 to-yellow-500 text-white rounded-xl font-semibold tracking-wide hover:from-orange-400 hover:to-yellow-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg"
    >
      {{ isSubmitting ? '登录中...' : 'LOGIN' }}
    </button>

    <!-- Register 链接 -->
    <div class="mt-8 text-center">
      <p class="text-gray-600 text-sm">
        Don't have an account?
        <router-link
          to="/register"
          class="ml-2 text-orange-500 hover:text-orange-600 font-semibold transition-colors"
        >
          Sign up now →
        </router-link>
      </p>
    </div>
  </form>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { useAuthStore } from '@/stores/auth'
import { debounce } from '@/utils/debounce'
import { EMAIL_REGEX } from '@/utils/validation'
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import Captcha from './Captcha.vue'

interface LoginFormData {
  email: string
  password: string
  captcha_id: string
  captcha_answer: string
}

const formData = reactive<LoginFormData>({
  email: '',
  password: '',
  captcha_id: '',
  captcha_answer: '',
})

const errors = reactive<Partial<Record<keyof LoginFormData, string>>>({})
const isSubmitting = ref(false)
const previewLoading = ref(false)
const isPreviewRequesting = ref(false) // 防止并发预览请求
const isValidatingCaptcha = ref(false) // 正在验证验证码，防止重复调用预览API
const captchaRef = ref<InstanceType<typeof Captcha> | null>(null)
const router = useRouter()
const authStore = useAuthStore()
const showPassword = ref(false)

// 记录最后一次成功预览的账号密码，用于判断是否应该清除头像
const lastSuccessfulPreview = ref<{ email: string; password: string } | null>(
  null
)

// 验证码验证去重机制：同一验证码300ms内只验证一次
let lastValidationCaptcha = ''
let lastValidationTimestamp = 0
const VALIDATION_DEBOUNCE_MS = 300

// handleCaptchaUpdate去重机制：防止同一事件被多次处理
let lastCaptchaUpdateKey = ''
let lastCaptchaUpdateTimestamp = 0
const CAPTCHA_UPDATE_DEBOUNCE_MS = 100

// 实时验证状态
const isEmailValid = computed(() => {
  const valid =
    formData.email && EMAIL_REGEX.test(formData.email) && !errors.email
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'LoginForm.vue:267',
      message: 'isEmailValid computed',
      data: { email: formData.email, valid, hasError: !!errors.email },
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: 'D',
    }),
  }).catch(() => {})
  // #endregion
  return valid
})

const isPasswordValid = computed(() => {
  const valid =
    formData.password && formData.password.length >= 8 && !errors.password
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'LoginForm.vue:271',
      message: 'isPasswordValid computed',
      data: {
        passwordLength: formData.password?.length,
        valid,
        hasError: !!errors.password,
      },
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: 'D',
    }),
  }).catch(() => {})
  // #endregion
  return valid
})

const isCaptchaValid = computed(() => {
  // 只有当验证码输入完整、没有错误、且已经通过实时校验时才显示打勾
  // 注意：实时校验是异步的，所以这里只检查基本条件
  const valid =
    formData.captcha_answer &&
    formData.captcha_answer.length === 4 &&
    !errors.captcha_answer
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'LoginForm.vue:277',
      message: 'isCaptchaValid computed',
      data: {
        captchaAnswer: formData.captcha_answer,
        captchaAnswerLength: formData.captcha_answer?.length,
        captchaId: formData.captcha_id,
        valid,
        hasError: !!errors.captcha_answer,
        errorMsg: errors.captcha_answer,
      },
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: 'A',
    }),
  }).catch(() => {})
  // #endregion
  return valid
})

// 验证码是否已通过校验（用于显示打勾图标）
const isCaptchaVerified = computed(() => {
  return (
    isCaptchaValid.value &&
    !errors.captcha_answer &&
    formData.captcha_answer.length === 4
  )
})

// 按钮禁用状态（综合所有验证条件）
const buttonDisabled = computed(() => {
  const disabled =
    isSubmitting.value ||
    !isEmailValid.value ||
    !isPasswordValid.value ||
    !isCaptchaValid.value ||
    !formData.captcha_id
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'LoginForm.vue:307',
      message: 'buttonDisabled computed',
      data: {
        isSubmitting: isSubmitting.value,
        isEmailValid: isEmailValid.value,
        isPasswordValid: isPasswordValid.value,
        isCaptchaValid: isCaptchaValid.value,
        hasCaptchaId: !!formData.captcha_id,
        disabled,
      },
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: 'A',
    }),
  }).catch(() => {})
  // #endregion
  return disabled
})

const emit = defineEmits<{
  'preview-success': [data: { displayName: string; avatar: string }]
  'preview-clear': []
}>()

// 验证邮箱格式（本地验证，不覆盖导入的validateEmail函数）
const validateEmailLocal = () => {
  if (formData.email && !EMAIL_REGEX.test(formData.email)) {
    errors.email = 'Please enter a valid email address'
  } else {
    errors.email = ''
  }
}

const handleEmailInput = () => {
  validateEmailLocal()
  // 如果邮箱变化，检查是否需要清除头像
  if (
    lastSuccessfulPreview.value &&
    formData.email !== lastSuccessfulPreview.value.email
  ) {
    // 邮箱变化，清除头像
    emit('preview-clear')
    lastSuccessfulPreview.value = null
  }
  // 重要：如果当前有验证码错误或频率限制错误，不应该触发预览（避免429错误）
  // 重要：如果正在验证验证码，不应该触发预览（避免重复调用API）
  const hasCaptchaRelatedError =
    errors.captcha_answer &&
    (errors.captcha_answer.includes('验证码错误') ||
      errors.captcha_answer.includes('频率限制') ||
      errors.captcha_answer.includes('请求过于频繁'))

  if (!hasCaptchaRelatedError && !isValidatingCaptcha.value) {
    debouncedTriggerPreview()
  }
}

const handlePasswordInput = () => {
  // 如果密码变化，检查是否需要清除头像
  if (
    lastSuccessfulPreview.value &&
    formData.password !== lastSuccessfulPreview.value.password
  ) {
    // 密码变化，清除头像
    emit('preview-clear')
    lastSuccessfulPreview.value = null
  }
  // 重要：如果当前有验证码错误或频率限制错误，不应该触发预览（避免429错误）
  // 重要：如果正在验证验证码，不应该触发预览（避免重复调用API）
  const hasCaptchaRelatedError =
    errors.captcha_answer &&
    (errors.captcha_answer.includes('验证码错误') ||
      errors.captcha_answer.includes('频率限制') ||
      errors.captcha_answer.includes('请求过于频繁'))

  if (!hasCaptchaRelatedError && !isValidatingCaptcha.value) {
    debouncedTriggerPreview()
  }
}

const handleCaptchaUpdate = async (data: {
  captcha_id: string
  captcha_answer: string
}) => {
  // 去重检查：防止同一事件被多次处理（100ms内）
  // 重要：必须在日志之前检查，避免重复处理
  const updateKey = `${data.captcha_id}:${data.captcha_answer}`
  const now = Date.now()
  if (
    updateKey &&
    updateKey === lastCaptchaUpdateKey &&
    now - lastCaptchaUpdateTimestamp < CAPTCHA_UPDATE_DEBOUNCE_MS
  ) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'LoginForm.vue:457',
        message: 'handleCaptchaUpdate early return - duplicate event',
        data: {
          updateKey,
          lastCaptchaUpdateKey,
          timeSinceLastUpdate: now - lastCaptchaUpdateTimestamp,
          willSkip: true,
        },
        timestamp: Date.now(),
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'B',
      }),
    }).catch(() => {})
    // #endregion
    return
  }

  // 立即更新去重标记（在日志之前），防止重复调用
  lastCaptchaUpdateKey = updateKey
  lastCaptchaUpdateTimestamp = now

  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'LoginForm.vue:474',
      message: 'handleCaptchaUpdate entry',
      data: {
        oldCaptchaId: formData.captcha_id,
        newCaptchaId: data.captcha_id,
        newCaptchaAnswer: data.captcha_answer,
        newCaptchaAnswerLength: data.captcha_answer?.length,
      },
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: 'B',
    }),
  }).catch(() => {})
  // #endregion
  // 只有当captcha_id真正改变时才更新
  const captchaIdChanged =
    data.captcha_id && data.captcha_id !== formData.captcha_id
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'LoginForm.vue:381',
      message: 'handleCaptchaUpdate captchaIdChanged',
      data: {
        captchaIdChanged,
        oldCaptchaId: formData.captcha_id,
        newCaptchaId: data.captcha_id,
      },
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: 'B',
    }),
  }).catch(() => {})
  // #endregion
  if (captchaIdChanged) {
    formData.captcha_id = data.captcha_id
    // 重要：如果captcha_id改变（验证码刷新），且当前有验证码错误或频率限制错误，不应该触发预览
    // 因为验证码刷新通常是因为验证码错误，此时不应该触发预览API（避免429错误）
    // 检查是否有错误提示，如果有，直接返回，避免执行后面的预览逻辑
    const hasErrorBeforeUpdate =
      errors.captcha_answer &&
      (errors.captcha_answer.includes('验证码错误') ||
        errors.captcha_answer.includes('频率限制') ||
        errors.captcha_answer.includes('请求过于频繁'))
    if (hasErrorBeforeUpdate && !data.captcha_answer) {
      // 验证码刷新且之前有错误，不应该触发预览
      formData.captcha_answer = ''
      errors.captcha_answer = errors.captcha_answer // 保持错误提示
      return
    }
  }

  // 更新验证码答案
  const currentValue = data.captcha_answer.toUpperCase()
  const oldCaptchaAnswer = formData.captcha_answer
  formData.captcha_answer = currentValue

  // 如果验证码刷新了（captcha_answer为空），清空之前的输入
  if (!data.captcha_answer) {
    // 清除去重标记，允许刷新后重新验证
    if (oldCaptchaAnswer !== currentValue) {
      lastValidationCaptcha = ''
      lastValidationTimestamp = 0
    }
    formData.captcha_answer = ''
    // 验证码刷新时，保持错误提示可见，直到用户重新输入
    // 注意：刷新验证码后不应该触发预览API，因为验证码答案已清空
    // 但是：如果头像已显示，应该保持显示（验证码刷新不影响头像）
    // 只有在验证码错误时刷新，才保持错误提示；如果是正常刷新，清除错误提示
    const hadCaptchaError = errors.captcha_answer?.includes('验证码错误')
    const hadRateLimitError =
      errors.captcha_answer?.includes('请求过于频繁') ||
      errors.captcha_answer?.includes('频率限制')

    if (!hadCaptchaError && !hadRateLimitError) {
      // 正常刷新验证码（不是错误导致的刷新），清除错误提示
      errors.captcha_answer = ''
    } else {
      // 如果是验证码错误或频率限制导致的刷新，保持错误提示
      // 但如果是频率限制，更新为更友好的提示
      if (hadRateLimitError) {
        errors.captcha_answer = '请求过于频繁，请稍后再试'
      }
      // 重要：验证码错误或频率限制导致的刷新，不应该触发预览API
      // 因为刷新验证码通常是因为验证码错误，此时不应该触发预览API（避免429错误）
    }
    // 验证码刷新后，不应该触发预览API（避免429错误）
    // 因为刷新验证码通常是因为验证码错误，此时不应该触发预览API
    return
  } else {
    // 处理验证码输入逻辑
    if (currentValue.length < 4) {
      // 如果输入长度小于4，清除错误提示（允许用户重新输入）
      // 但如果是验证码错误提示，保持显示（用户需要看到错误信息）
      if (
        errors.captcha_answer &&
        !errors.captcha_answer.includes('验证码错误')
      ) {
        errors.captcha_answer = ''
      }
    } else if (currentValue.length === 4) {
      // 如果输入了4位验证码，立即校验
      // 重要：如果之前有验证码错误或频率限制错误，用户重新输入验证码时，应该清除错误提示
      // 这样用户才能重新验证（否则会一直阻止API调用）
      const hadCaptchaError = errors.captcha_answer?.includes('验证码错误')
      const hadRateLimitError =
        errors.captcha_answer?.includes('请求过于频繁') ||
        errors.captcha_answer?.includes('频率限制')
      // #region agent log
      fetch(
        'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'LoginForm.vue:456',
            message: 'captcha input 4 chars',
            data: {
              currentValue,
              hadCaptchaError,
              hadRateLimitError,
              errorBefore: errors.captcha_answer,
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'C',
          }),
        }
      ).catch(() => {})
      // #endregion

      // 用户重新输入验证码，清除之前的错误提示（允许重新验证）
      // 重要：只有在用户重新输入验证码时，才清除错误提示并允许重新验证
      // 这样可以避免在验证码错误后，刷新验证码时触发额外的API调用
      // 重要：清除所有错误提示，包括429错误，允许用户重新验证
      errors.captcha_answer = ''
      // #region agent log
      fetch(
        'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'LoginForm.vue:587',
            message: 'clearing captcha error before validation',
            data: {
              hadError: hadCaptchaError || hadRateLimitError,
              clearedError: true,
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'C',
          }),
        }
      ).catch(() => {})
      // #endregion

      // 设置标志：正在验证验证码，防止在验证期间触发额外的预览API调用
      isValidatingCaptcha.value = true

      // 实时校验验证码（无论是正常输入还是测试用的错误验证码）
      // 重要：validateCaptchaRealTime 内部会调用 previewLogin API，所以这里不需要再次触发预览
      // 重要：在验证期间，阻止其他预览API调用（通过isValidatingCaptcha标志）
      await validateCaptchaRealTime()

      // 清除标志：验证完成
      isValidatingCaptcha.value = false
      // #region agent log
      fetch(
        'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'LoginForm.vue:598',
            message: 'after validateCaptchaRealTime - validation complete',
            data: {
              errorAfter: errors.captcha_answer,
              isValidatingCaptcha: isValidatingCaptcha.value,
              captchaAnswer: formData.captcha_answer,
              captchaAnswerLength: formData.captcha_answer?.length,
              isCaptchaValid: isCaptchaValid.value,
              buttonDisabled: buttonDisabled.value,
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'A',
          }),
        }
      ).catch(() => {})
      // #endregion
      // #region agent log
      fetch(
        'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'LoginForm.vue:475',
            message: 'after validateCaptchaRealTime',
            data: {
              errorAfter: errors.captcha_answer,
              isValidatingCaptcha: isValidatingCaptcha.value,
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'C',
          }),
        }
      ).catch(() => {})
      // #endregion

      // 如果验证码正确（没有错误），触发预览（如果邮箱和密码已填写）
      // 但是：如果当前有验证码错误或频率限制错误，不应该触发预览（避免429错误）
      const hasError =
        errors.captcha_answer &&
        (errors.captcha_answer.includes('验证码错误') ||
          errors.captcha_answer.includes('频率限制') ||
          errors.captcha_answer.includes('请求过于频繁'))

      // 重要：如果验证码错误，不应该触发预览（避免429错误）
      // 因为验证码错误时，预览API会返回400错误，不需要再次调用预览API
      // 注意：validateCaptchaRealTime 内部已经调用了 previewLogin API，所以这里不需要再次触发预览
      // 如果验证码正确，validateCaptchaRealTime 内部已经处理了预览逻辑
      // 如果验证码错误，validateCaptchaRealTime 已经设置了错误提示，不应该再次调用API
      // 重要：输入4位验证码后，validateCaptchaRealTime已经处理了所有逻辑，应该直接返回，避免执行后面的代码导致重复调用
      return
    } else if (currentValue.length < 4) {
      // 如果输入长度小于4，清除之前的验证标记（允许重新验证）
      // 这样当用户重新输入时，可以再次验证
      // 注意：验证码长度改变，清除去重标记，允许重新验证
      lastValidationCaptcha = ''
      lastValidationTimestamp = 0
    }
  }

  // 如果邮箱和密码已填写，且captcha_id已更新，触发预览
  // 根据PRD，预览时验证码可选，所以即使验证码答案为空也可以触发预览
  // 注意：验证码刷新后（captcha_answer为空）也应该触发预览（因为预览时验证码可选）
  // 但是：如果验证码错误，不应该触发预览（因为验证码错误时，预览API会返回400错误）
  // 而且：如果captcha_id刚改变（刷新验证码），且当前有验证码错误提示，不应该触发预览
  // 因为刷新验证码通常是因为验证码错误，此时不应该触发预览API（避免429错误）
  // 而且：如果429错误（频率限制），不应该触发预览（避免触发更多API调用）
  // 重要：如果当前有任何验证码相关错误（验证码错误或频率限制），不应该触发预览
  // 重要：如果captcha_id刚改变（刷新验证码），不应该触发预览（避免429错误）
  // 因为验证码刷新通常是因为验证码错误，此时不应该触发预览API
  // 重要：如果正在验证验证码，不应该触发预览（避免重复调用API）
  // 重要：如果captcha_answer为空（验证码刚刷新），不应该触发预览（避免429错误）
  const hasCaptchaRelatedError =
    errors.captcha_answer &&
    (errors.captcha_answer.includes('验证码错误') ||
      errors.captcha_answer.includes('频率限制') ||
      errors.captcha_answer.includes('请求过于频繁'))

  // 如果captcha_id刚改变（刷新验证码），不应该触发预览（避免429错误）
  // 因为验证码刷新通常是因为验证码错误，此时不应该触发预览API
  const shouldSkipPreviewAfterRefresh = captchaIdChanged

  // 如果验证码答案为空（刚刷新），不应该触发预览（避免429错误）
  const isCaptchaJustRefreshed =
    !formData.captcha_answer || formData.captcha_answer.length === 0

  if (
    formData.email &&
    formData.password &&
    formData.captcha_id &&
    !hasCaptchaRelatedError &&
    !shouldSkipPreviewAfterRefresh &&
    !isValidatingCaptcha.value && // 如果正在验证验证码，不触发预览（避免重复调用）
    !isCaptchaJustRefreshed // 如果验证码刚刷新，不触发预览（避免429错误）
  ) {
    debouncedTriggerPreview()
  }
}

// 刷新验证码（通过captchaRef调用组件的refreshCaptcha方法）
const refreshCaptcha = async () => {
  if (captchaRef.value) {
    await captchaRef.value.refreshCaptcha()
  }
}

// 验证码实时校验 - 使用预览API来验证验证码（因为预览API会验证验证码）
const validateCaptchaRealTime = async () => {
  // 去重检查：同一验证码300ms内只验证一次
  // 重要：必须在函数入口处立即检查，避免重复调用
  const currentCaptcha = `${formData.captcha_id}:${formData.captcha_answer}`
  const now = Date.now()
  if (
    currentCaptcha &&
    currentCaptcha === lastValidationCaptcha &&
    now - lastValidationTimestamp < VALIDATION_DEBOUNCE_MS
  ) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'LoginForm.vue:791',
        message: 'validateCaptchaRealTime early return - duplicate call',
        data: {
          currentCaptcha,
          lastValidationCaptcha,
          timeSinceLastValidation: now - lastValidationTimestamp,
          willSkip: true,
        },
        timestamp: Date.now(),
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'C',
      }),
    }).catch(() => {})
    // #endregion
    return
  }

  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      location: 'LoginForm.vue:548',
      message: 'validateCaptchaRealTime entry',
      data: {
        captchaId: formData.captcha_id,
        captchaAnswer: formData.captcha_answer,
        captchaAnswerLength: formData.captcha_answer?.length,
        email: formData.email,
        password: formData.password,
        lastValidationCaptcha,
        timeSinceLastValidation: Date.now() - lastValidationTimestamp,
      },
      timestamp: Date.now(),
      sessionId: 'debug-session',
      runId: 'run1',
      hypothesisId: 'C',
    }),
  }).catch(() => {})
  // #endregion

  // 基本条件检查
  if (
    !formData.captcha_id ||
    !formData.captcha_answer ||
    formData.captcha_answer.length !== 4
  ) {
    // 基本条件不满足，不更新去重标记（允许条件满足后重新验证）
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'LoginForm.vue:559',
        message: 'validateCaptchaRealTime early return - basic check failed',
        data: {
          hasCaptchaId: !!formData.captcha_id,
          hasCaptchaAnswer: !!formData.captcha_answer,
          captchaAnswerLength: formData.captcha_answer?.length,
        },
        timestamp: Date.now(),
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'B',
      }),
    }).catch(() => {})
    // #endregion
    return
  }

  // 基本条件满足，立即更新去重标记（在API调用之前），防止重复调用
  // 重要：必须在基本条件检查之后更新，这样只有满足条件的调用才会被去重
  lastValidationCaptcha = currentCaptcha
  lastValidationTimestamp = now

  // 重要：如果当前有验证码错误或频率限制错误，不应该再次调用API（避免429错误）
  // 用户需要先清除错误提示（通过重新输入验证码）才能再次验证
  // 特别重要：如果已经有429错误（频率限制），绝对不应该再次调用API
  const hasError =
    errors.captcha_answer &&
    (errors.captcha_answer.includes('验证码错误') ||
      errors.captcha_answer.includes('频率限制') ||
      errors.captcha_answer.includes('请求过于频繁'))

  if (hasError) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'LoginForm.vue:573',
        message: 'validateCaptchaRealTime early return - has error',
        data: { errorMsg: errors.captcha_answer },
        timestamp: Date.now(),
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'C',
      }),
    }).catch(() => {})
    // #endregion
    // 有错误时，不调用API，直接返回
    // 特别重要：429错误必须完全阻止后续API调用
    return
  }

  // 额外检查：如果isPreviewRequesting为true，说明有预览请求正在进行，不应该重复调用
  if (isPreviewRequesting.value) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'LoginForm.vue:583',
        message: 'validateCaptchaRealTime early return - preview requesting',
        data: { isPreviewRequesting: isPreviewRequesting.value },
        timestamp: Date.now(),
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'C',
      }),
    }).catch(() => {})
    // #endregion
    return
  }

  // 如果邮箱和密码都已填写，使用预览API来验证验证码
  // 预览API会验证验证码，如果验证码错误会返回INVALID_CAPTCHA错误（400状态码）
  // 如果验证码正确但密码错误，会返回valid: false（200状态码）
  // 注意：如果只输入验证码没有账号密码，无法验证（这是设计限制，因为验证码验证需要账号密码）
  // 但是：即使没有账号密码，只要验证码输入了4位且没有错误，也应该允许按钮启用（基本验证通过）
  // 因为PRD要求的是：验证码输入完整（4位）且没有错误，就可以启用按钮
  // 重要：如果邮箱或密码为空，无法调用API验证，但基本条件（4位且无错误）已满足，应该允许按钮启用
  if (formData.email && formData.password) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'LoginForm.vue:596',
        message: 'validateCaptchaRealTime calling previewLogin API',
        data: {
          email: formData.email,
          hasPassword: !!formData.password,
          captchaId: formData.captcha_id,
          captchaAnswer: formData.captcha_answer,
        },
        timestamp: Date.now(),
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'C',
      }),
    }).catch(() => {})
    // #endregion
    try {
      // 调用预览API，它会验证验证码
      // 注意：去重标记已在函数入口处更新，这里不需要再次更新
      const result = await authStore.previewLogin({
        email: formData.email,
        password: formData.password,
        captcha_id: formData.captcha_id,
        captcha_answer: formData.captcha_answer,
      })

      // 如果API调用成功（没有抛出错误），说明验证码是正确的
      // 无论valid是true还是false，只要没有抛出错误，就说明验证码验证通过了
      // 验证码正确，清除错误提示（包括429错误）
      // 重要：必须清除所有错误，包括429错误，这样按钮才能启用
      const hadErrorBefore = !!errors.captcha_answer
      errors.captcha_answer = ''
      // #region agent log
      fetch(
        'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'LoginForm.vue:900',
            message: 'validateCaptchaRealTime API success - captcha valid',
            data: {
              valid: result?.valid,
              hasUser: !!result?.user,
              hadErrorBefore,
              clearedError: true,
              captchaAnswer: formData.captcha_answer,
              isCaptchaValid: isCaptchaValid.value,
              buttonDisabled: buttonDisabled.value,
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'C',
          }),
        }
      ).catch(() => {})
      // #endregion
    } catch (error: any) {
      // #region agent log
      fetch(
        'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'LoginForm.vue:615',
            message: 'validateCaptchaRealTime API error',
            data: {
              statusCode: error?.response?.status,
              errorCode: error?.response?.data?.code,
              errorMessage: error?.response?.data?.error,
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'C',
          }),
        }
      ).catch(() => {})
      // #endregion
      // 如果抛出错误，检查是否是验证码错误
      const errorCode = error?.response?.data?.code || ''
      // #region agent log
      fetch(
        'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            location: 'LoginForm.vue:850',
            message: 'validateCaptchaRealTime error handling',
            data: {
              errorCode,
              statusCode: error?.response?.status,
              errorMessage: error?.response?.data?.error,
              willSetError: errorCode === 'INVALID_CAPTCHA',
            },
            timestamp: Date.now(),
            sessionId: 'debug-session',
            runId: 'run1',
            hypothesisId: 'C',
          }),
        }
      ).catch(() => {})
      // #endregion
      const errorMessage = error?.response?.data?.error || error?.message || ''
      const statusCode = error?.response?.status || 0

      // 如果是429错误（频率限制），显示用户友好的提示
      if (statusCode === 429) {
        // 429错误：频率限制，显示提示信息
        // 不清除头像，也不刷新验证码，但给用户提示
        // 重要：设置错误提示后，后续的预览API调用应该被阻止
        errors.captcha_answer = '请求过于频繁，请稍后再试'
        // #region agent log
        fetch(
          'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              location: 'LoginForm.vue:898',
              message: 'validateCaptchaRealTime 429 error - rate limited',
              data: {
                statusCode: 429,
                setError: '请求过于频繁，请稍后再试',
                willBlockButton: true,
              },
              timestamp: Date.now(),
              sessionId: 'debug-session',
              runId: 'run1',
              hypothesisId: 'C',
            }),
          }
        ).catch(() => {})
        // #endregion
        // 不清除验证码错误提示（如果有），但显示频率限制提示
        // 不刷新验证码，避免触发更多API调用
        // 重要：429错误不应该刷新验证码，因为验证码可能是正确的，只是请求太频繁
        return
      }

      // 只有明确是验证码错误（INVALID_CAPTCHA）时，才显示验证码错误提示
      // 重要：必须明确是验证码错误（400状态码 + INVALID_CAPTCHA错误码），才刷新验证码
      // 其他错误（如网络错误、账号密码错误等）不应该刷新验证码
      if (
        statusCode === 400 &&
        (errorCode === 'INVALID_CAPTCHA' || errorMessage.includes('验证码错误'))
      ) {
        // 验证码错误，设置错误提示
        // 重要：不要立即刷新验证码，因为用户可能输入的是正确的验证码
        // 如果立即刷新，会删除旧验证码，导致用户无法再次验证
        // 只有在用户手动刷新验证码时，才删除旧验证码
        errors.captcha_answer = '验证码错误，请重新输入或刷新验证码'
        // #region agent log
        fetch(
          'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              location: 'LoginForm.vue:1095',
              message:
                'validateCaptchaRealTime INVALID_CAPTCHA error - NOT refreshing',
              data: {
                statusCode: 400,
                errorCode,
                errorMessage,
                captchaId: formData.captcha_id,
                captchaAnswer: formData.captcha_answer,
                willRefresh: false,
                reason: 'Do not auto-refresh to allow user to retry',
              },
              timestamp: Date.now(),
              sessionId: 'debug-session',
              runId: 'run1',
              hypothesisId: 'C',
            }),
          }
        ).catch(() => {})
        // #endregion

        // 不清空验证码输入，允许用户重新输入或手动刷新
        // 不清除去重标记，允许用户重新验证
        // 不自动刷新验证码，让用户手动刷新（如果用户认为验证码看不清）
      } else {
        // 其他错误（网络错误、账号密码错误等），不影响验证码校验
        // 验证码可能是正确的，只是其他原因导致错误
        // 不清除验证码错误提示（如果有），也不设置新的错误
        // 重要：不清除errors.captcha_answer，保持之前的状态
        // 如果之前有429错误，保持429错误提示
        // 如果之前没有错误，保持无错误状态
        // #region agent log
        fetch(
          'http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              location: 'LoginForm.vue:950',
              message:
                'validateCaptchaRealTime other error - not captcha error',
              data: {
                statusCode,
                errorCode,
                errorMessage,
                currentError: errors.captcha_answer,
                willNotRefresh: true,
              },
              timestamp: Date.now(),
              sessionId: 'debug-session',
              runId: 'run1',
              hypothesisId: 'C',
            }),
          }
        ).catch(() => {})
        // #endregion
      }
    }
  } else {
    // 如果邮箱或密码为空，无法验证验证码，但基本条件（4位且无错误）已满足
    // 根据PRD，只要验证码输入完整（4位）且没有错误，就可以启用按钮
    // 所以这里不需要设置错误，保持errors.captcha_answer为空即可
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/ee7fc425-3c65-463c-bae6-3f8112f51957', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        location: 'LoginForm.vue:960',
        message: 'validateCaptchaRealTime - no email/password, cannot verify',
        data: {
          hasEmail: !!formData.email,
          hasPassword: !!formData.password,
          captchaAnswerLength: formData.captcha_answer?.length,
          currentError: errors.captcha_answer,
        },
        timestamp: Date.now(),
        sessionId: 'debug-session',
        runId: 'run1',
        hypothesisId: 'C',
      }),
    }).catch(() => {})
    // #endregion
    // 如果之前没有错误，确保errors.captcha_answer为空，允许按钮启用
    // 如果之前有错误（比如验证码错误），保持错误提示
    if (
      errors.captcha_answer &&
      !errors.captcha_answer.includes('验证码错误') &&
      !errors.captcha_answer.includes('频率限制') &&
      !errors.captcha_answer.includes('请求过于频繁')
    ) {
      // 如果不是验证码相关的错误，清除错误提示
      errors.captcha_answer = ''
    }
  }
}

// 触发登录预览（实时验证）
const triggerPreview = async () => {
  if (
    !formData.email ||
    !formData.password ||
    isSubmitting.value ||
    previewLoading.value
  ) {
    return
  }

  // 如果没有captcha_id，无法调用预览API（后端要求captcha_id必填）
  // 但captcha_answer可以为空（根据PRD，预览时验证码可选）
  if (!formData.captcha_id) {
    return
  }

  // 如果已有预览请求在进行，跳过本次请求（防止429错误）
  if (isPreviewRequesting.value) {
    return
  }

  // 重要：如果正在验证验证码，不应该触发预览（避免重复调用API）
  // validateCaptchaRealTime已经会调用预览API，这里不应该重复调用
  if (isValidatingCaptcha.value) {
    return
  }

  previewLoading.value = true
  isPreviewRequesting.value = true

  try {
    // 调用预览API，验证账号密码
    // 根据PRD和测试用例TC-AUTH_PREVIEW-010，预览时验证码答案可以为空
    const result = await authStore.previewLogin({
      email: formData.email,
      password: formData.password,
      captcha_id: formData.captcha_id,
      captcha_answer: formData.captcha_answer || '', // 如果为空，传空字符串
    })

    if (result.valid) {
      // 预览成功，记录最后一次成功预览的账号密码
      lastSuccessfulPreview.value = {
        email: formData.email,
        password: formData.password,
      }

      // 触发预览成功事件
      emit('preview-success', {
        displayName: result.user?.display_name || '',
        avatar: result.user?.avatar_url || '',
      })
    } else {
      // 预览失败（账号密码错误），清除头像
      // 但是：如果当前有验证码错误提示或频率限制提示，说明可能是验证码错误或频率限制导致的，不应该清除头像
      // 因为验证码错误时，预览API会返回400错误（不会进入这里）
      // 但为了安全，如果当前有验证码相关错误提示，不清除头像
      const hasCaptchaRelatedError =
        errors.captcha_answer &&
        (errors.captcha_answer.includes('验证码错误') ||
          errors.captcha_answer.includes('频率限制') ||
          errors.captcha_answer.includes('请求过于频繁'))

      if (!hasCaptchaRelatedError) {
        emit('preview-clear')
        lastSuccessfulPreview.value = null
      }
    }
  } catch (error: any) {
    // 验证码错误由validateCaptchaRealTime处理，这里只处理其他错误
    const errorCode = error?.response?.data?.code || ''
    const errorMessage = error?.response?.data?.error || error?.message || ''
    const statusCode = error?.response?.status || 0

    // 如果是429错误（频率限制），显示用户友好的提示，不清除头像
    if (statusCode === 429) {
      // 429错误：频率限制，显示提示信息
      // 不清除头像，但给用户提示
      // 重要：设置错误提示后，后续的预览API调用应该被阻止
      errors.captcha_answer = '请求过于频繁，请稍后再试'
      return
    }

    // 如果是验证码错误（400状态码 + INVALID_CAPTCHA错误码 或 错误消息包含"验证码"），不清除头像
    // 因为验证码错误时，validateCaptchaRealTime已经处理了，这里不应该清除头像
    const isCaptchaError =
      statusCode === 400 &&
      (errorCode === 'INVALID_CAPTCHA' || errorMessage.includes('验证码'))

    if (!isCaptchaError) {
      // 只有非验证码错误时才清除头像（如网络错误、账号密码错误等）
      emit('preview-clear')
      lastSuccessfulPreview.value = null
    }
  } finally {
    previewLoading.value = false
    isPreviewRequesting.value = false
  }
}

// 防抖处理的预览触发函数（避免频繁调用API）
// 防抖时间设置为3000ms（3秒），确保不会触发频率限制（每分钟10次）
// 重要：validateCaptchaRealTime也会调用预览API，所以防抖时间要足够长
// 重要：在验证码验证期间（isValidatingCaptcha为true），不应该触发预览API
const debouncedTriggerPreview = debounce(
  (...args: Parameters<typeof triggerPreview>) => {
    // 再次检查是否正在验证验证码（防抖期间可能已经开始验证）
    if (!isValidatingCaptcha.value) {
    triggerPreview(...args)
    }
  },
  3000
)

// 登录表单提交处理
const handleSubmit = async () => {
  // 验证表单字段
  if (!formData.email) {
    errors.email = '请输入邮箱'
    return
  }
  if (!EMAIL_REGEX.test(formData.email)) {
    errors.email = '请输入有效的邮箱地址'
    return
  }
  if (!formData.password) {
    errors.password = '请输入密码'
    return
  }
  if (formData.password.length < 8) {
    errors.password = '密码长度至少为8位'
    return
  }
  if (!formData.captcha_id) {
    errors.captcha_answer = '请先获取验证码'
    return
  }
  if (!formData.captcha_answer || formData.captcha_answer.length !== 4) {
    errors.captcha_answer = '请输入4位验证码'
    return
  }

  // 使用与buttonDisabled相同的验证逻辑，确保一致性
  if (
    isSubmitting.value ||
    !isEmailValid.value ||
    !isPasswordValid.value ||
    !isCaptchaValid.value ||
    !formData.captcha_id
  ) {
    return
  }

  isSubmitting.value = true

  try {
    // 提交登录请求
    await authStore.login({
      email: formData.email,
      password: formData.password,
      captcha_id: formData.captcha_id,
      captcha_answer: formData.captcha_answer,
    })

    // 登录成功，跳转到首页
    router.push('/')
  } catch (error: any) {
    // 处理登录错误
    const errorCode = error?.response?.data?.code || ''
    const errorMessage =
      error?.response?.data?.error || error?.message || '登录失败，请重试'

    if (errorCode === 'INVALID_CAPTCHA') {
      errors.captcha_answer = '验证码错误，请重新输入'
      // 刷新验证码
      await refreshCaptcha()
    } else if (errorCode === 'INVALID_CREDENTIALS') {
      errors.password = '邮箱或密码错误'
    } else {
      errors.email = errorMessage
    }
  } finally {
    isSubmitting.value = false
  }
}

// 密码输入框失焦处理
const handlePasswordBlur = () => {
  // 密码输入框失焦后，如果邮箱和密码都已填写，触发预览
  // 根据PRD，预览时验证码可选，但需要captcha_id（验证码组件加载时会自动设置）
  // 使用防抖处理，避免频繁触发（与输入事件共享防抖）
  // 重要：如果当前有验证码错误或频率限制错误，不应该触发预览（避免429错误）
  // 重要：如果正在验证验证码，不应该触发预览（避免重复调用API）
  const hasCaptchaRelatedError =
    errors.captcha_answer &&
    (errors.captcha_answer.includes('验证码错误') ||
      errors.captcha_answer.includes('频率限制') ||
      errors.captcha_answer.includes('请求过于频繁'))

  if (
    formData.email &&
    formData.password &&
    formData.captcha_id &&
    !hasCaptchaRelatedError &&
    !isValidatingCaptcha.value // 如果正在验证验证码，不触发预览（避免重复调用）
  ) {
    // 即使验证码答案为空，也可以触发预览（预览时验证码可选）
    // 使用防抖，避免与输入事件的防抖冲突
    debouncedTriggerPreview()
  } else if (formData.email && formData.password) {
    // 如果验证码还没加载，等待验证码加载后再触发预览
    // 这会在handleCaptchaUpdate中处理
  }
}
</script>
