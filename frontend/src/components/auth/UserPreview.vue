<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div class="user-preview">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="displayName" class="user-info">
      <DefaultAvatar
        :avatar-url="avatarUrl"
        :avatar-letter="avatarLetter"
        :user-name="displayName"
        size="large"
        shape="circle"
      />
      <span class="display-name">{{ displayName }}</span>
    </div>
  </div>
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
  color: #6b7280;
  font-size: 0.875rem;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.display-name {
  font-size: 1rem;
  font-weight: 500;
  color: #1f2937;
}
</style>
