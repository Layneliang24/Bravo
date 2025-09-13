<template>
  <div class="blog-detail" role="main">
    <nav class="breadcrumb" role="navigation" aria-label="面包屑导航">
      <a href="/blog" aria-label="返回博客列表">← 返回博客列表</a>
    </nav>

    <article class="blog-post">
      <header class="post-header">
        <h1 data-testid="blog-detail-title">{{ post.title }}</h1>
        <div class="post-meta">
          <time :datetime="post.createdAt" aria-label="发布时间">{{ formatDate(post.createdAt) }}</time>
          <span class="category" aria-label="分类">{{ post.category }}</span>
        </div>
      </header>

      <div class="post-content" data-testid="blog-detail-content">
        <p>{{ post.content }}</p>
      </div>

      <footer class="post-footer">
        <div class="post-actions" data-testid="blog-actions">
          <button
            data-testid="edit-button"
            @click="editPost"
            class="edit-button"
            aria-label="编辑博客"
          >
            编辑
          </button>
          <button
            data-testid="delete-button"
            @click="deletePost"
            class="delete-button"
            aria-label="删除博客"
          >
            删除
          </button>
        </div>
      </footer>
    </article>

    <!-- 编辑表单（隐藏状态，用于测试） -->
    <div v-if="showEditForm" class="edit-form" data-testid="edit-form">
      <input
        type="text"
        placeholder="博客标题"
        data-testid="post-title"
        v-model="editForm.title"
        aria-label="博客标题"
      />
      <textarea
        placeholder="博客内容"
        data-testid="post-content"
        v-model="editForm.content"
        aria-label="博客内容"
      ></textarea>
      <button
        data-testid="publish-button"
        @click="publishPost"
        class="publish-button"
        aria-label="发布博客"
      >
        发布
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()

// SEO meta 标签
onMounted(() => {
  // 动态设置页面标题和 meta 标签
  document.title = `${post.value.title} - Bravo 博客`

  // 添加 Open Graph 标签
  const ogTitle = document.querySelector('meta[property="og:title"]')
  if (!ogTitle) {
    const meta = document.createElement('meta')
    meta.setAttribute('property', 'og:title')
    meta.setAttribute('content', `${post.value.title} - Bravo 博客`)
    document.head.appendChild(meta)
  }

  const ogDescription = document.querySelector('meta[property="og:description"]')
  if (!ogDescription) {
    const meta = document.createElement('meta')
    meta.setAttribute('property', 'og:description')
    meta.setAttribute('content', post.value.content.substring(0, 160))
    document.head.appendChild(meta)
  }
})

// 模拟博客数据
const mockPosts = [
  {
    id: 1,
    title: '测试博客标题 1',
    content: '这是测试博客 1 的内容。包含一些测试文本用于验证功能。这里有很多内容来测试博客详情页面的显示效果。',
    category: '技术',
    createdAt: '2024-01-15T10:00:00Z'
  },
  {
    id: 2,
    title: '测试博客标题 2',
    content: '这是测试博客 2 的内容。包含一些测试文本用于验证功能。这里有很多内容来测试博客详情页面的显示效果。',
    category: '生活',
    createdAt: '2024-01-14T15:30:00Z'
  },
  {
    id: 3,
    title: '测试博客标题 3',
    content: '这是测试博客 3 的内容。包含一些测试文本用于验证功能。这里有很多内容来测试博客详情页面的显示效果。',
    category: '随笔',
    createdAt: '2024-01-13T09:15:00Z'
  }
]

// 根据路由参数获取博客详情
const postId = parseInt(route.params.id as string)

// 尝试从 localStorage 获取用户创建的博客
let foundPost = mockPosts.find(p => p.id === postId)

if (!foundPost) {
  try {
    const storedPosts = JSON.parse(localStorage.getItem('mockBlogPosts') || '[]') as BlogPost[]
    foundPost = storedPosts.find((p: BlogPost) => p.id === postId)
  } catch (error) {
    // console.warn('无法从 localStorage 读取博客:', error)
  }
}

const post = ref(foundPost || mockPosts[0])

const showEditForm = ref(false)

// 编辑表单数据
const editForm = reactive({
  title: post.value.title,
  content: post.value.content
})

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const editPost = () => {
  // console.log('编辑博客')
  showEditForm.value = true
  editForm.title = post.value.title
  editForm.content = post.value.content
}

const publishPost = () => {
  // console.log('发布博客:', editForm.title, editForm.content)
  post.value.title = editForm.title
  post.value.content = editForm.content
  showEditForm.value = false
}

const deletePost = () => {
  // console.log('删除博客')
  if (confirm('确定要删除这篇博客吗？')) {
    router.push('/blog')
  }
}
</script>

<style scoped>
.blog-detail {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.breadcrumb {
  margin-bottom: 2rem;
}

.breadcrumb a {
  color: #409eff;
  text-decoration: none;
  font-size: 0.9rem;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.blog-post {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.post-header {
  padding: 2rem;
  border-bottom: 1px solid #eee;
}

.post-header h1 {
  margin: 0 0 1rem 0;
  color: #333;
  font-size: 2rem;
  line-height: 1.3;
}

.post-meta {
  display: flex;
  gap: 1rem;
  color: #666;
  font-size: 0.9rem;
}

.category {
  background: #f0f0f0;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.post-content {
  padding: 2rem;
  line-height: 1.6;
  color: #444;
}

.post-content p {
  margin: 0 0 1rem 0;
}

.post-footer {
  padding: 1rem 2rem;
  background: #f9f9f9;
  border-top: 1px solid #eee;
}

.post-actions {
  display: flex;
  gap: 0.5rem;
}

.edit-form {
  margin: 2rem 0;
  padding: 2rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.edit-form input,
.edit-form textarea {
  width: 100%;
  padding: 0.75rem;
  margin: 0.5rem 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 1rem;
}

.edit-form textarea {
  height: 150px;
  resize: vertical;
}

.edit-button {
  padding: 0.5rem 1rem;
  background-color: #e6a23c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 0.5rem;
}

.edit-button:hover {
  background-color: #b88230;
}

.delete-button {
  padding: 0.5rem 1rem;
  background-color: #f56c6c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.delete-button:hover {
  background-color: #c45656;
}

.publish-button {
  padding: 0.75rem 1.5rem;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  margin-top: 1rem;
}

.publish-button:hover {
  background-color: #529b2e;
}
</style>
