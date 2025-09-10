<template>
  <div class="blog">
    <h1 data-testid="blog-title">博客</h1>
    <div data-testid="blog-list">
      <div
        v-for="post in mockPosts"
        :key="post.id"
        class="blog-item"
        data-testid="blog-item"
      >
        <h3>{{ post.title }}</h3>
        <p>{{ post.content }}</p>
      </div>
    </div>

    <!-- 搜索功能 -->
    <div class="search-section">
      <input
        type="text"
        placeholder="搜索博客..."
        data-testid="search-input"
        v-model="searchKeyword"
      />
      <button
        data-testid="search-button"
        @click="searchBlog"
      >
        搜索
      </button>
    </div>

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
import { ref, reactive } from 'vue'

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

const searchBlog = () => {
  console.log('搜索博客:', searchKeyword.value)
}

const filterByCategory = () => {
  console.log('按分类筛选:', selectedCategory.value)
}

const createPost = () => {
  console.log('创建新博客')
}

const loadMore = () => {
  console.log('加载更多博客')
}
</script>

<style scoped>
.blog {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

.blog-item {
  border: 1px solid #ddd;
  padding: 1rem;
  margin: 1rem 0;
  border-radius: 8px;
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
</style>
