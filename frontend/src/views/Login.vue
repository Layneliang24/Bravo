<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="login-view">
    <!-- 背景图片 -->
    <div class="background-image"></div>

    <!-- 装饰性椭圆元素 -->
    <div class="decorative-ellipse ellipse-1"></div>
    <div class="decorative-ellipse ellipse-2"></div>
    <div class="decorative-ellipse ellipse-3"></div>

    <div class="login-container">
      <!-- 玻璃态卡片 -->
      <div class="glass-card">
        <h1 class="main-title">Login</h1>
        <div class="divider"></div>
        <p class="subtitle">Welcome onboard with us!</p>
        <LoginForm />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import LoginForm from '@/components/auth/LoginForm.vue'
</script>

<style scoped>
/* Glassmorphism 设计 - 根据实际截图优化 */
.login-view {
  min-height: 100vh;
  background: #1a1a1a;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  overflow: hidden;
}

/* 背景 */
.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #1a1a1a;
  z-index: 0;
}

/* 装饰性椭圆元素 - 左上角白色圆形 */
.decorative-ellipse {
  position: absolute;
  border-radius: 50%;
  z-index: 1;
}

.ellipse-1 {
  width: 100px;
  height: 100px;
  top: 20px;
  left: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: transparent;
}

.ellipse-2 {
  display: none;
}

.ellipse-3 {
  display: none;
}

.login-container {
  position: relative;
  z-index: 2;
  width: 100%;
  max-width: 479px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 玻璃态卡片 - 深灰色，蓝色边框发光效果 */
.glass-card {
  width: 479px;
  min-height: 497px;
  background: rgba(50, 50, 50, 0.85);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  border-radius: 27px;
  border: 1px solid rgba(100, 150, 255, 0.4);
  padding: 2rem 2.5rem;
  box-shadow:
    0 0 30px rgba(100, 150, 255, 0.3),
    0 8px 32px 0 rgba(0, 0, 0, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

/* 主标题 "Login" - 40px, Iceland 字体, 白色 */
.main-title {
  font-family: 'Iceland', sans-serif;
  font-size: 40px;
  font-weight: 400;
  line-height: 38.8px;
  color: rgb(255, 255, 255);
  margin: 0 0 0.5rem 0;
  text-align: left;
}

/* 分隔线 */
.divider {
  width: 110px;
  height: 1px;
  background: rgb(255, 255, 255);
  margin-bottom: 1rem;
}

/* 副标题 "Welcome onboard with us!" - 20px, Montserrat Light, 白色 */
.subtitle {
  font-family: 'Montserrat', sans-serif;
  font-size: 20px;
  font-weight: 300;
  line-height: 24.38px;
  color: rgb(255, 255, 255);
  margin: 0 0 2rem 0;
  text-align: left;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .glass-card {
    width: 100%;
    max-width: 479px;
    padding: 1.5rem;
  }

  .main-title {
    font-size: 32px;
  }

  .subtitle {
    font-size: 18px;
  }

  .decorative-ellipse {
    display: none;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .glass-card {
    width: 90%;
    max-width: 479px;
  }
}
</style>
