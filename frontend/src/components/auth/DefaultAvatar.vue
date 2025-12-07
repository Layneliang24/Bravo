<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div
    class="default-avatar"
    :class="[
      `size-${size}`,
      `shape-${shape}`,
      $attrs.class,
    ]"
  >
    <img
      v-if="hasAvatarUrl"
      :src="avatarUrl"
      :alt="altText"
      @error="handleImageError"
    />
    <span v-else class="avatar-letter">{{ avatarLetter }}</span>
  </div>
</template>

<script setup lang="ts">
// REQ-ID: REQ-2025-003-user-login
import { computed, ref } from 'vue'

interface Props {
  avatarUrl?: string | null
  avatarLetter: string
  size?: 'small' | 'medium' | 'large'
  shape?: 'circle' | 'square'
}

const props = withDefaults(defineProps<Props>(), {
  avatarUrl: null,
  size: 'medium',
  shape: 'circle',
})

const imageError = ref(false)

const hasAvatarUrl = computed(() => {
  return props.avatarUrl && props.avatarUrl.trim() !== '' && !imageError.value
})

const altText = computed(() => {
  return `用户头像 - ${props.avatarLetter}`
})

const handleImageError = () => {
  imageError.value = true
}
</script>

<style scoped>
.default-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background-color: #3b82f6;
  color: white;
  font-weight: 600;
  overflow: hidden;
}

/* 尺寸 */
.size-small {
  width: 2rem;
  height: 2rem;
  font-size: 0.75rem;
}

.size-medium {
  width: 3rem;
  height: 3rem;
  font-size: 1rem;
}

.size-large {
  width: 4rem;
  height: 4rem;
  font-size: 1.5rem;
}

/* 形状 */
.shape-circle {
  border-radius: 50%;
}

.shape-square {
  border-radius: 0.375rem;
}

/* 图片样式 */
.default-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 首字母样式 */
.avatar-letter {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  text-transform: uppercase;
  user-select: none;
}
</style>
