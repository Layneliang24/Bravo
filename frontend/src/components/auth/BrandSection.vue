<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="brand-section" data-testid="brand-section">
    <!-- Logo区域 -->
    <div class="logo-section">
      <div class="logo-icon">
        <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
          <defs>
            <linearGradient
              id="logoGradient"
              x1="0"
              y1="0"
              x2="56"
              y2="56"
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stop-color="#ff8904" />
              <stop offset="100%" stop-color="#fdd700" />
            </linearGradient>
            <linearGradient
              id="englishGradient"
              x1="0"
              y1="0"
              x2="36"
              y2="36"
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stop-color="#ff8904" />
              <stop offset="100%" stop-color="#fdd700" />
            </linearGradient>
            <linearGradient
              id="codingGradient"
              x1="0"
              y1="0"
              x2="36"
              y2="36"
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stop-color="#05df72" />
              <stop offset="100%" stop-color="#00d492" />
            </linearGradient>
            <linearGradient
              id="careerGradient"
              x1="0"
              y1="0"
              x2="36"
              y2="36"
              gradientUnits="userSpaceOnUse"
            >
              <stop offset="0%" stop-color="#51a2ff" />
              <stop offset="100%" stop-color="#00b8db" />
            </linearGradient>
          </defs>
          <rect width="56" height="56" rx="14" fill="url(#logoGradient)" />
          <path
            d="M28 18L34 28L28 38L22 28L28 18Z"
            fill="white"
            opacity="0.9"
          />
        </svg>
      </div>
      <div class="logo-text">
        <h2 class="logo-title">Learning Hub</h2>
        <p class="logo-subtitle">Grow Every Day</p>
      </div>
    </div>

    <!-- 欢迎文字 -->
    <div class="welcome-text">
      <p>
        Welcome to your personal learning space for English, Coding, and Career
        Growth
      </p>
    </div>

    <!-- 中央插图 -->
    <div class="illustration" data-testid="illustration">
      <div class="illustration-circle">
        <div class="gradient-square orange"></div>
        <div class="gradient-square green"></div>
        <div class="gradient-square blue"></div>
        <div class="dots">
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
          <span class="dot"></span>
        </div>
      </div>
    </div>

    <!-- 功能卡片 -->
    <div class="feature-cards">
      <div
        class="feature-card"
        data-testid="feature-card"
        v-for="feature in features"
        :key="feature.id"
      >
        <div class="feature-icon" :class="feature.iconClass">
          <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
            <rect width="36" height="36" rx="14" :fill="feature.iconGradient" />
            <path :d="feature.iconPath" fill="white" opacity="0.9" />
          </svg>
        </div>
        <div class="feature-content">
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
        </div>
      </div>
      <!-- SVG渐变定义（全局） -->
      <svg width="0" height="0" style="position: absolute">
        <defs>
          <linearGradient
            id="englishGradient"
            x1="0"
            y1="0"
            x2="36"
            y2="36"
            gradientUnits="userSpaceOnUse"
          >
            <stop offset="0%" stop-color="#ff8904" />
            <stop offset="100%" stop-color="#fdd700" />
          </linearGradient>
          <linearGradient
            id="codingGradient"
            x1="0"
            y1="0"
            x2="36"
            y2="36"
            gradientUnits="userSpaceOnUse"
          >
            <stop offset="0%" stop-color="#05df72" />
            <stop offset="100%" stop-color="#00d492" />
          </linearGradient>
          <linearGradient
            id="careerGradient"
            x1="0"
            y1="0"
            x2="36"
            y2="36"
            gradientUnits="userSpaceOnUse"
          >
            <stop offset="0%" stop-color="#51a2ff" />
            <stop offset="100%" stop-color="#00b8db" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { ref } from 'vue'

const features = ref([
  {
    id: 1,
    title: 'English Learning',
    description: 'Master English skills',
    iconClass: 'english',
    iconGradient: 'url(#englishGradient)',
    iconPath: 'M18 10L20 16L18 22L16 16L18 10Z',
  },
  {
    id: 2,
    title: 'Coding Practice',
    description: 'Build coding skills',
    iconClass: 'coding',
    iconGradient: 'url(#codingGradient)',
    iconPath: 'M12 12L18 18L12 24L6 18L12 12Z',
  },
  {
    id: 3,
    title: 'Career Growth',
    description: 'Advance your career',
    iconClass: 'career',
    iconGradient: 'url(#careerGradient)',
    iconPath: 'M18 8L22 14L18 20L14 14L18 8Z',
  },
])
</script>

<style scoped>
.brand-section {
  width: var(--brand-section-width);
  height: 100%;
  padding: var(--spacing-brand-padding);
  display: flex;
  flex-direction: column;
  gap: 32px;
  background: transparent;
}

/* Logo区域 */
.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 56.179px;
  height: 56.179px;
  flex-shrink: 0;
}

.logo-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.logo-title {
  font-family: var(--font-family);
  font-size: 16px;
  font-weight: bold;
  line-height: 20px;
  color: var(--text-primary);
  margin: 0;
}

.logo-subtitle {
  font-family: var(--font-family);
  font-size: 14px;
  font-weight: 400;
  line-height: 20px;
  color: var(--text-link);
  margin: 0;
}

/* 欢迎文字 */
.welcome-text {
  margin-top: 8px;
}

.welcome-text p {
  font-family: var(--font-family);
  font-size: var(--font-size-subtitle);
  font-weight: 400;
  line-height: 26px;
  color: var(--text-secondary);
  margin: 0;
}

/* 中央插图 */
.illustration {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 256px;
  margin: 16px 0;
}

.illustration-circle {
  position: relative;
  width: 256px;
  height: 256px;
  border-radius: 50%;
  border: 2px solid rgba(249, 115, 22, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
}

.gradient-square {
  position: absolute;
  width: 80px;
  height: 80px;
  border-radius: 12px;
  opacity: 0.8;
}

.gradient-square.orange {
  background: linear-gradient(
    135deg,
    rgba(255, 137, 4, 1) 0%,
    rgba(253, 199, 0, 1) 100%
  );
  top: 20%;
  left: 20%;
}

.gradient-square.green {
  background: linear-gradient(
    135deg,
    rgba(5, 223, 114, 1) 0%,
    rgba(0, 212, 146, 1) 100%
  );
  top: 20%;
  right: 20%;
}

.gradient-square.blue {
  background: linear-gradient(
    135deg,
    rgba(81, 162, 255, 1) 0%,
    rgba(0, 184, 219, 1) 100%
  );
  bottom: 20%;
  left: 50%;
  transform: translateX(-50%);
}

.dots {
  position: absolute;
  width: 100%;
  height: 100%;
}

.dot {
  position: absolute;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary-orange);
  opacity: 0.6;
}

.dot:nth-child(1) {
  top: 30%;
  left: 10%;
}

.dot:nth-child(2) {
  top: 10%;
  right: 30%;
}

.dot:nth-child(3) {
  bottom: 30%;
  right: 10%;
}

.dot:nth-child(4) {
  bottom: 10%;
  left: 30%;
}

/* 功能卡片 */
.feature-cards {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-feature-gap);
  margin-top: auto;
}

.feature-card {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 60px;
  padding: 12px 16px;
  border-radius: var(--input-border-radius);
  background: var(--bg-feature-english);
  transition: transform 0.2s ease;
}

.feature-card:nth-child(2) {
  background: var(--bg-feature-coding);
}

.feature-card:nth-child(3) {
  background: var(--bg-feature-career);
}

.feature-card:hover {
  transform: translateY(-2px);
}

.feature-icon {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
}

.feature-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.feature-title {
  font-family: var(--font-family);
  font-size: var(--font-size-label);
  font-weight: bold;
  line-height: var(--line-height-label);
  color: var(--text-primary);
  margin: 0;
}

.feature-description {
  font-family: var(--font-family);
  font-size: 12px;
  font-weight: 400;
  line-height: 16px;
  color: var(--text-secondary);
  margin: 0;
}

/* SVG渐变定义 */
:deep(svg defs) {
  display: block;
}
</style>
