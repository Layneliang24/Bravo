<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="verify-email-view">
    <!-- 验证中 -->
    <div v-if="isVerifying" class="verification-loading">
      <div class="loading-spinner"></div>
      <p class="loading-text">验证中...</p>
    </div>

    <!-- 没有token -->
    <div v-else-if="!token" class="verification-error">
      <div class="error-icon">❌</div>
      <h2 class="error-title">无效的验证链接</h2>
      <p class="error-message">验证链接无效，请检查链接是否正确或重新申请验证邮件。</p>
      <button @click="handleGoToLogin" class="login-button">前往登录</button>
    </div>

    <!-- 验证成功 -->
    <div v-else-if="verificationResult === 'success'" class="verification-success">
      <div class="success-icon">✅</div>
      <h2 class="success-title">邮箱验证成功！</h2>
      <p class="success-message">{{ successMessage }}</p>
      <p class="auto-redirect-hint">页面将在3秒后自动跳转到登录页面...</p>
      <button @click="handleGoToLogin" class="login-button">立即前往登录</button>
    </div>

    <!-- 验证失败 -->
    <div v-else-if="verificationResult === 'error'" class="verification-error">
      <div class="error-icon">❌</div>
      <h2 class="error-title">邮箱验证失败</h2>
      <p class="error-message">{{ errorMessage }}</p>
      <div class="error-actions">
        <button @click="handleGoToLogin" class="login-button">前往登录</button>
        <p class="resend-hint">
          验证链接可能已过期或无效，请前往登录页面重新发送或重新申请验证邮件。
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// 从URL获取token
const token = computed(() => {
  const tokenParam = route.query.token
  return typeof tokenParam === 'string' ? tokenParam : null
})

// 验证状态
const isVerifying = ref(false)
const verificationResult = ref<'success' | 'error' | null>(null)
const successMessage = ref('')
const errorMessage = ref('')

// 执行邮箱验证
const verifyEmail = async () => {
  if (!token.value) {
    verificationResult.value = 'error'
    errorMessage.value = '无效的验证链接'
    return
  }

  isVerifying.value = true
  verificationResult.value = null
  errorMessage.value = ''
  successMessage.value = ''

  try {
    const response = await authStore.verifyEmail(token.value)

    if (response && response.message) {
      verificationResult.value = 'success'
      successMessage.value = response.message || '邮箱验证成功，您现在可以登录了'
      // 验证成功后3秒自动跳转到登录页
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    } else {
      verificationResult.value = 'error'
      errorMessage.value = '邮箱验证失败，请稍后重试'
    }
  } catch (error: any) {
    verificationResult.value = 'error'
    errorMessage.value =
      error?.message || '验证链接已过期或无效，请重新申请验证邮件'
  } finally {
    isVerifying.value = false
  }
}

// 跳转到登录页
const handleGoToLogin = () => {
  router.push('/login')
}

// 组件挂载时自动验证
onMounted(() => {
  verifyEmail()
})
</script>

<style scoped>
.verify-email-view {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  background-color: #f9fafb;
}

.verification-loading,
.verification-success,
.verification-error {
  max-width: 500px;
  width: 100%;
  padding: 3rem;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  text-align: center;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  margin: 0 auto 1rem;
  border: 4px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-text {
  font-size: 1rem;
  color: #6b7280;
}

.success-icon,
.error-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.success-title,
.error-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1rem;
}

.success-title {
  color: #059669;
}

.error-title {
  color: #dc2626;
}

.success-message,
.error-message {
  font-size: 1rem;
  color: #4b5563;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.login-button {
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

.login-button:hover {
  background-color: #2563eb;
}

.error-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.resend-hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin-top: 0.5rem;
  line-height: 1.6;
}

.auto-redirect-hint {
  font-size: 0.875rem;
  color: #6b7280;
  margin-bottom: 1rem;
  font-style: italic;
}
</style>
