<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="forgot-password-view">
    <div class="auth-card" data-testid="auth-card">
      <!-- 左侧品牌展示区 -->
      <BrandSection />

      <!-- 分隔线 -->
      <div class="divider-line"></div>

      <!-- 右侧表单区 -->
      <div class="form-section" data-testid="form-section">
        <div class="form-header">
          <h1 class="form-title">Forgot Password</h1>
          <p class="form-subtitle">Enter your email to receive a password reset link</p>
        </div>
        <PasswordResetForm />
        <div class="auth-link">
          <span>Remember your password?</span>
          <router-link to="/login">Sign in</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import PasswordResetForm from '@/components/auth/PasswordResetForm.vue'
import BrandSection from '@/components/auth/BrandSection.vue'
</script>

<style scoped>
/* 复用登录页面的样式 */
.forgot-password-view {
  min-height: 100vh;
  background: linear-gradient(
    135deg,
    rgba(255, 247, 237, 0.3) 0%,
    rgba(240, 253, 244, 0.3) 50%,
    rgba(239, 246, 255, 0.3) 100%
  );
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  overflow: auto;
}

.auth-card {
  width: var(--main-container-width);
  min-height: var(--main-container-height);
  background: var(--bg-main-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 0.667px solid rgba(255, 255, 255, 0.5);
  box-shadow: var(--shadow-main-card);
  display: flex;
  overflow: hidden;
  position: relative;
}

.auth-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(
    90deg,
    rgba(249, 115, 22, 0.5) 0%,
    rgba(234, 179, 8, 0.5) 33.333%,
    rgba(34, 197, 94, 0.5) 66.667%,
    rgba(249, 115, 22, 0.5) 100%
  );
  z-index: 1;
}

.divider-line {
  width: 2px;
  height: 100%;
  background: var(--border-divider);
  flex-shrink: 0;
}

.form-section {
  width: var(--form-section-width);
  padding: var(--spacing-container-padding);
  display: flex;
  flex-direction: column;
  gap: 32px;
  position: relative;
  z-index: 1;
}

.form-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-title {
  font-family: var(--font-family);
  font-size: var(--font-size-title);
  font-weight: bold;
  line-height: var(--line-height-title);
  letter-spacing: 0.5px;
  color: var(--text-primary);
  margin: 0;
}

.form-subtitle {
  font-family: var(--font-family);
  font-size: var(--font-size-subtitle);
  font-weight: 400;
  line-height: var(--line-height-subtitle);
  color: var(--text-secondary);
  margin: 0;
}

.auth-link {
  text-align: center;
  font-family: var(--font-family);
  font-size: var(--font-size-label);
  color: var(--text-secondary);
  margin-top: 16px;
}

.auth-link a {
  color: var(--text-link);
  font-weight: bold;
  text-decoration: none;
  margin-left: 8px;
  transition: opacity 0.2s ease;
}

.auth-link a:hover {
  opacity: 0.8;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .forgot-password-view {
    padding: 1rem;
  }

  .auth-card {
    width: 100%;
    max-width: 100%;
    min-height: auto;
    flex-direction: column;
  }

  .divider-line {
    width: 100%;
    height: 2px;
  }

  .form-section {
    width: 100%;
    padding: 2rem 1.5rem;
  }
}
</style>
