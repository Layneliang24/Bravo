<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <Transition name="fade">
    <div v-if="loading || displayName" class="user-preview">
      <Transition name="fade" mode="out-in">
        <div v-if="loading" key="loading" class="loading">
          <span class="loading-spinner"></span>
          <span>加载中...</span>
        </div>
        <div v-else-if="displayName" key="user" class="user-info">
          <DefaultAvatar
            :avatar-url="avatarUrl"
            :avatar-letter="avatarLetter"
            :user-name="displayName"
            size="large"
            shape="circle"
          />
          <span class="display-name">{{ displayName }}</span>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import DefaultAvatar from './DefaultAvatar.vue'

interface Props {
  displayName?: string | null
  avatarUrl?: string | null
  avatarLetter?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  displayName: null,
  avatarUrl: null,
  avatarLetter: '',
  loading: false,
})
</script>

<style scoped>
.user-preview {
  width: 100%;
  padding: 1rem;
  text-align: center;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid #e5e7eb;
  border-top-color: var(--color-primary-gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  animation: fadeInScale 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: translateY(-10px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.display-name {
  font-size: 1rem;
  font-weight: 500;
  color: #1f2937;
}

/* 淡入淡出过渡动画 */
.fade-enter-active {
  transition: opacity 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
