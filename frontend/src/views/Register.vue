<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="register-view">
    <div class="register-container">
      <!-- 移动端：单列全屏布局 -->
      <div class="register-content mobile-layout">
        <div class="register-form-wrapper">
          <h1 class="register-title">创建账户</h1>
          <RegisterForm />
          <div class="auth-link">
            <span>已有账户？</span>
            <router-link to="/login">立即登录</router-link>
          </div>
        </div>
      </div>

      <!-- 桌面端：左右分栏布局 -->
      <div class="register-content desktop-layout">
        <div class="brand-section">
          <div class="brand-content">
            <h1 class="brand-title">Bravo</h1>
            <p class="brand-subtitle">加入我们，开启智能学习之旅</p>
            <div class="brand-features">
              <div class="feature-item">
                <span class="feature-icon">📚</span>
                <span class="feature-text">丰富内容</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🎯</span>
                <span class="feature-text">精准学习</span>
              </div>
              <div class="feature-item">
                <span class="feature-icon">🚀</span>
                <span class="feature-text">快速成长</span>
              </div>
            </div>
          </div>
        </div>
        <div class="form-section">
          <div class="register-form-wrapper">
            <h1 class="register-title">创建账户</h1>
            <RegisterForm />
            <div class="auth-link">
              <span>已有账户？</span>
              <router-link to="/login">立即登录</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import RegisterForm from '@/components/auth/RegisterForm.vue'
</script>

<style scoped>
.register-view {
  min-height: 100vh;
  background: var(--gradient-background);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.register-container {
  width: 100%;
  max-width: 1440px;
}

/* 移动端布局（默认） */
.mobile-layout {
  display: block;
}

.desktop-layout {
  display: none;
}

.register-content {
  width: 100%;
}

.register-form-wrapper {
  background: var(--input-background);
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: var(--box-shadow-lg);
  animation: fadeInUp 0.5s ease-out;
}

.register-title {
  font-size: 1.875rem;
  font-weight: 700;
  color: var(--color-primary-dark-blue);
  text-align: center;
  margin-bottom: 2rem;
}

.auth-link {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.auth-link a {
  color: var(--color-primary-gold);
  text-decoration: none;
  font-weight: 500;
  margin-left: 0.5rem;
  transition: color 0.3s ease;
}

.auth-link a:hover {
  color: var(--color-primary-dark-blue);
  text-decoration: underline;
}

/* 品牌展示区域（桌面端） */
.brand-section {
  display: none;
}

.brand-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  padding: 3rem;
  color: var(--text-light);
  text-align: center;
  animation: fadeIn 0.8s ease-out;
}

.brand-title {
  font-size: 4rem;
  font-weight: 800;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, var(--text-light) 0%, var(--color-primary-gold) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.brand-subtitle {
  font-size: 1.5rem;
  margin-bottom: 3rem;
  opacity: 0.9;
}

.brand-features {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 300px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--border-radius);
  backdrop-filter: blur(10px);
  animation: fadeInLeft 0.6s ease-out;
  animation-fill-mode: both;
}

.feature-item:nth-child(1) {
  animation-delay: 0.2s;
}

.feature-item:nth-child(2) {
  animation-delay: 0.4s;
}

.feature-item:nth-child(3) {
  animation-delay: 0.6s;
}

.feature-icon {
  font-size: 2rem;
}

.feature-text {
  font-size: 1.125rem;
  font-weight: 500;
}

/* 响应式断点：768px */
@media (min-width: 768px) {
  .register-form-wrapper {
    padding: 3rem;
    max-width: 500px;
    margin: 0 auto;
  }

  .register-title {
    font-size: 2.25rem;
  }
}

/* 响应式断点：1024px - 桌面端左右分栏 */
@media (min-width: 1024px) {
  .mobile-layout {
    display: none;
  }

  .desktop-layout {
    display: flex;
    min-height: 80vh;
    border-radius: 1rem;
    overflow: hidden;
    box-shadow: var(--box-shadow-lg);
  }

  .brand-section {
    display: flex;
    flex: 1;
    background: rgba(26, 35, 126, 0.3);
    backdrop-filter: blur(10px);
  }

  .form-section {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--input-background);
    padding: 3rem;
  }

  .register-form-wrapper {
    width: 100%;
    max-width: 450px;
    background: transparent;
    padding: 0;
    box-shadow: none;
  }
}

/* 响应式断点：1440px - 大屏幕优化 */
@media (min-width: 1440px) {
  .desktop-layout {
    min-height: 85vh;
  }

  .brand-content {
    padding: 4rem;
  }

  .brand-title {
    font-size: 5rem;
  }

  .brand-subtitle {
    font-size: 1.75rem;
  }

  .form-section {
    padding: 4rem;
  }
}

/* 淡入动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}
</style>
