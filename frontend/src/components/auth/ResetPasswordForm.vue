<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <form @submit.prevent="handleSubmit" class="reset-password-form">
    <div v-if="!token" class="error-message">
      无效的重置链接，请重新申请密码重置
    </div>
    <template v-else>
      <FloatingInput
        v-model="formData.password"
        label="新密码"
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
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
      <button type="submit" :disabled="isSubmitting" class="submit-button">
        {{ isSubmitting ? '重置中...' : '重置密码' }}
      </button>
    </template>
  </form>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { reactive, ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  validatePassword,
  validatePasswordConfirm,
} from '@/utils/validation'
import FloatingInput from './FloatingInput.vue'
import PasswordStrength from './PasswordStrength.vue'

interface FormData {
  password: string
  password_confirm: string
}

const formData = reactive<FormData>({
  password: '',
  password_confirm: '',
})

const errors = reactive<Partial<Record<keyof FormData, string>>>({})
const isSubmitting = ref(false)
const successMessage = ref('')
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 从URL获取token
const token = computed(() => {
  const tokenParam = route.query.token
  return typeof tokenParam === 'string' ? tokenParam : null
})

const handleSubmit = async () => {
  // 检查token
  if (!token.value) {
    return
  }

  // 清除之前的错误和成功消息
  errors.password = ''
  errors.password_confirm = ''
  successMessage.value = ''

  // 验证密码
  const passwordError = validatePassword(formData.password)
  if (passwordError) {
    errors.password = passwordError
    return
  }

  // 验证确认密码
  const passwordConfirmError = validatePasswordConfirm(
    formData.password,
    formData.password_confirm
  )
  if (passwordConfirmError) {
    errors.password_confirm = passwordConfirmError
    return
  }

  isSubmitting.value = true

  try {
    const response = await authStore.resetPassword({
      token: token.value,
      password: formData.password,
      password_confirm: formData.password_confirm,
    })

    if (response && response.message) {
      successMessage.value = response.message
      // 清空表单
      formData.password = ''
      formData.password_confirm = ''
      // 3秒后跳转到登录页
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    }
  } catch (error: any) {
    // 处理错误
    const errorMessage =
      error?.response?.data?.error || error?.message || '密码重置失败，请稍后重试'

    if (error?.response?.data?.code === 'PASSWORD_MISMATCH') {
      errors.password_confirm = '两次输入的密码不一致'
    } else if (error?.response?.data?.code === 'WEAK_PASSWORD') {
      errors.password = '密码长度至少为8位'
    } else if (error?.response?.data?.code === 'INVALID_TOKEN') {
      errors.password = '无效的重置链接，请重新申请密码重置'
    } else {
      errors.password = errorMessage
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.reset-password-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
}

.error-message {
  color: var(--color-error);
  font-size: 0.875rem;
  padding: 0.75rem;
  background-color: #fee2e2;
  border-radius: var(--border-radius);
  text-align: center;
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
