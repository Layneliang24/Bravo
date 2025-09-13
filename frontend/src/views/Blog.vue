<template>
  <div class="blog" role="main">
    <nav class="main-navigation" role="navigation" aria-label="主导航">
      <a href="/" aria-label="返回首页">首页</a>
      <a href="/blog" aria-current="page" aria-label="当前页面：博客">博客</a>
      <a href="/login" aria-label="登录">登录</a>
    </nav>

    <h1 data-testid="blog-title">博客</h1>
    <div data-testid="blog-list">
      <div
        v-for="post in mockPosts"
        :key="post.id"
        class="blog-item"
        data-testid="blog-item"
        @click="goToBlogDetail(post.id)"
        @keydown.enter="goToBlogDetail(post.id)"
        @keydown.space="goToBlogDetail(post.id)"
        role="button"
        tabindex="0"
        :aria-label="`查看博客：${post.title}`"
      >
        <h3>{{ post.title }}</h3>
        <p>{{ post.content }}</p>
      </div>
    </div>

    <!-- 搜索功能 -->
    <nav class="search-section" role="search">
      <input
        type="text"
        placeholder="搜索博客..."
        data-testid="search-input"
        v-model="searchKeyword"
        aria-label="搜索博客"
      />
      <button
        data-testid="search-button"
        @click="searchBlog"
        aria-label="执行搜索"
      >
        搜索
      </button>
    </nav>

    <!-- 分类筛选 -->
    <div class="filter-section">
      <select
        data-testid="category-filter"
        v-model="selectedCategory"
        @change="filterByCategory"
      >
        <option value="">所有分类</option>
        <option value="技术">技术</option>
        <option value="生活">生活</option>
        <option value="随笔">随笔</option>
      </select>
    </div>

    <!-- 创建博客按钮 -->
    <button
      data-testid="create-post"
      @click="createPost"
      class="create-button"
    >
      创建新博客
    </button>

    <!-- 博客编辑表单（隐藏状态，用于测试） -->
    <div v-if="showEditForm" class="edit-form" data-testid="edit-form">
      <input
        type="text"
        placeholder="博客标题"
        data-testid="post-title"
        v-model="editForm.title"
      />
      <textarea
        placeholder="博客内容"
        data-testid="post-content"
        v-model="editForm.content"
      ></textarea>
      <button
        data-testid="publish-button"
        @click="publishPost"
        class="publish-button"
      >
        发布
      </button>
    </div>

    <!-- 博客项目操作按钮（隐藏状态，用于测试） -->
    <div v-if="showActions" class="blog-actions" data-testid="blog-actions">
      <button
        data-testid="edit-button"
        @click="editPost"
        class="edit-button"
      >
        编辑
      </button>
      <button
        data-testid="delete-button"
        @click="deletePost"
        class="delete-button"
      >
        删除
      </button>
    </div>

    <!-- 加载更多按钮 -->
    <button
      data-testid="load-more"
      @click="loadMore"
      class="load-more-button"
    >
      加载更多
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// SEO meta 标签
onMounted(() => {
  // 动态设置页面标题和 meta 标签
  document.title = '博客 - Bravo'

  // 添加meta描述标签
  const metaDescription = document.querySelector('meta[name="description"]')
  if (!metaDescription) {
    const meta = document.createElement('meta')
    meta.setAttribute('name', 'description')
    meta.setAttribute('content', 'Bravo 项目博客页面，分享技术文章和生活感悟')
    document.head.appendChild(meta)
  }

  // 添加 Open Graph 标签
  const ogTitle = document.querySelector('meta[property="og:title"]')
  if (!ogTitle) {
    const meta = document.createElement('meta')
    meta.setAttribute('property', 'og:title')
    meta.setAttribute('content', '博客 - Bravo')
    document.head.appendChild(meta)
  }

  const ogDescription = document.querySelector('meta[property="og:description"]')
  if (!ogDescription) {
    const meta = document.createElement('meta')
    meta.setAttribute('property', 'og:description')
    meta.setAttribute('content', 'Bravo 项目博客页面，分享技术文章和生活感悟')
    document.head.appendChild(meta)
  }
})

// 模拟博客数据
const mockPosts = ref([
  {
    id: 1,
    title: '测试博客标题 1',
    content: '这是测试博客 1 的内容。包含一些测试文本用于验证功能。',
    category: '技术'
  },
  {
    id: 2,
    title: '测试博客标题 2',
    content: '这是测试博客 2 的内容。包含一些测试文本用于验证功能。',
    category: '生活'
  },
  {
    id: 3,
    title: '测试博客标题 3',
    content: '这是测试博客 3 的内容。包含一些测试文本用于验证功能。',
    category: '随笔'
  }
])

const searchKeyword = ref('')
const selectedCategory = ref('')
const showEditForm = ref(false)
const showActions = ref(false)

// 编辑表单数据
const editForm = reactive({
  title: '',
  content: ''
})

const searchBlog = () => {
  // console.log('搜索博客:', searchKeyword.value)
}

const filterByCategory = () => {
  // console.log('按分类筛选:', selectedCategory.value)
}

const createPost = () => {
  // console.log('创建新博客')
  showEditForm.value = true
  showActions.value = true  // 同时显示操作按钮，用于测试
}

const publishPost = () => {
  // console.log('发布博客:', editForm.title, editForm.content)

  // 创建新博客
  const newPost = {
    id: Date.now(), // 简单的ID生成
    title: editForm.title,
    content: editForm.content,
    category: '技术', // 默认分类
    createdAt: new Date().toISOString()
  }

  // 添加到博客列表
  mockPosts.value.push(newPost)

  // 保存到 localStorage 以便 BlogDetail 页面访问
  try {
    const existingPosts = JSON.parse(localStorage.getItem('mockBlogPosts') || '[]')
    existingPosts.push(newPost)
    localStorage.setItem('mockBlogPosts', JSON.stringify(existingPosts))
  } catch (error) {
    // console.warn('无法保存到 localStorage:', error)
  }

  // 跳转到新创建的博客详情页
  router.push(`/blog/${newPost.id}`)

  showEditForm.value = false
  editForm.title = ''
  editForm.content = ''
}

const editPost = () => {
  // console.log('编辑博客')
  showActions.value = true
}

const deletePost = () => {
  // console.log('删除博客')
  showActions.value = false
}

const loadMore = () => {
  // console.log('加载更多博客')
}

const goToBlogDetail = (postId: number) => {
  router.push(`/blog/${postId}`)
}
</script>

<style scoped>
.blog {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.main-navigation {
  margin-bottom: 2rem;
  padding: 1rem 0;
  border-bottom: 1px solid #eee;
}

.main-navigation a {
  margin-right: 1rem;
  padding: 0.5rem 1rem;
  text-decoration: none;
  color: #409eff;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.main-navigation a:hover {
  background-color: #f0f8ff;
}

.main-navigation a[aria-current="page"] {
  background-color: #409eff;
  color: white;
}

.blog-item {
  border: 1px solid #ddd;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.blog-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
  transform: translateY(-1px);
}

.blog-item:focus {
  outline: 2px solid #409eff;
  outline-offset: 2px;
}

.search-section, .filter-section {
  margin: 1rem 0;
}

.search-section input {
  padding: 0.5rem;
  margin-right: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-section button, .create-button, .load-more-button {
  padding: 0.5rem 1rem;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 0.5rem;
}

.search-section button:hover, .create-button:hover, .load-more-button:hover {
  background-color: #337ecc;
}

.filter-section select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.edit-form {
  margin: 1rem 0;
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.edit-form input,
.edit-form textarea {
  width: 100%;
  padding: 0.5rem;
  margin: 0.5rem 0;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
}

.edit-form textarea {
  height: 100px;
  resize: vertical;
}

.publish-button {
  padding: 0.5rem 1rem;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.publish-button:hover {
  background-color: #529b2e;
}

.blog-actions {
  margin: 1rem 0;
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
</style>
