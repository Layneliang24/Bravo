<!-- REQ-ID: REQ-2025-003-user-login -->
<template>
  <div
    class="default-avatar"
    :class="[
      `size-${size}`,
      `shape-${shape}`,
      $attrs.class,
    ]"
    role="img"
    :aria-label="ariaLabel"
  >
    <img
      v-if="hasAvatarUrl"
      :src="avatarUrl"
      :alt="altText"
      @error="handleImageError"
      @load="handleImageLoad"
    />
    <span v-else class="avatar-letter" aria-hidden="true">{{
      avatarLetter
    }}</span>
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
  userName?: string
}

const props = withDefaults(defineProps<Props>(), {
  avatarUrl: null,
  size: 'medium',
  shape: 'circle',
  userName: '',
})

const imageError = ref(false)

const hasAvatarUrl = computed(() => {
  return (
    props.avatarUrl &&
    props.avatarUrl.trim() !== '' &&
    !imageError.value
  )
})

const altText = computed(() => {
  if (props.userName) {
    return `${props.userName}的头像`
  }
  return `用户头像 - ${props.avatarLetter}`
})

const ariaLabel = computed(() => {
  if (props.userName) {
    return `${props.userName}的头像`
  }
  return `用户头像，首字母${props.avatarLetter}`
})

const handleImageError = () => {
  imageError.value = true
}

const handleImageLoad = () => {
  imageError.value = false
}
</script>

<style scoped>
.default-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-button);
  color: white;
  font-weight: 600;
  overflow: hidden;
  flex-shrink: 0;
}

/* 尺寸 */
.size-small {
  width: 2rem;
  height: 2rem;
  min-width: 2rem;
  min-height: 2rem;
  font-size: 0.75rem;
}

.size-medium {
  width: 3rem;
  height: 3rem;
  min-width: 3rem;
  min-height: 3rem;
  font-size: 1rem;
}

.size-large {
  width: 4rem;
  height: 4rem;
  min-width: 4rem;
  min-height: 4rem;
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
  display: block;
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
  line-height: 1;
}
</style>
