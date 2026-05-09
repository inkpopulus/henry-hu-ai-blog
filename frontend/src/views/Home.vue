<template>
  <div>
    <div v-if="searchQuery" class="search-state fade-in">
      搜索 "{{ searchQuery }}" 的结果（{{ posts.length }} 篇）
      <a href="#" @click.prevent="clearSearch" class="clear-link">清除搜索</a>
    </div>

    <div v-if="tags.length" class="tags-filter fade-in">
      <span class="tags-filter-label">标签筛选</span>
      <div class="tag-select" ref="selectRef">
        <div class="tag-select-input" @click="dropdownOpen = !dropdownOpen">
          <span v-if="activeTag" class="tag active" @click.stop="clearTag">
            {{ activeTag }} ✕
          </span>
          <span v-else class="tag-select-placeholder">选择标签...</span>
          <svg class="tag-select-arrow" :class="{ open: dropdownOpen }" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
        </div>
        <div v-if="dropdownOpen" class="tag-dropdown">
          <input
            v-model="tagSearch"
            class="tag-dropdown-search"
            placeholder="搜索标签..."
            @click.stop
            ref="searchInput"
          />
          <div class="tag-dropdown-list">
            <div
              v-for="t in filteredTags"
              :key="t"
              class="tag-dropdown-item"
              :class="{ active: t === activeTag }"
              @click="selectTag(t)"
            >
              {{ t }}
            </div>
            <div v-if="filteredTags.length === 0" class="tag-dropdown-empty">
              没有匹配的标签
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="loading" class="state-empty">
      <p>加载中...</p>
    </div>

    <div v-else-if="posts.length === 0" class="state-empty">
      <div class="icon">📝</div>
      <p>{{ searchQuery ? '没有找到匹配的文章' : '暂无文章，去写一篇吧' }}</p>
    </div>

    <div v-else class="post-list">
      <div
        v-for="(post, i) in posts"
        :key="post.id"
        class="card post-card fade-in"
        :class="`fade-in-delay-${i + 1}`"
        @click="$router.push(`/post/${post.id}`)"
      >
        <h2>{{ post.title }}</h2>
        <div class="meta">{{ post.created_at }}</div>
        <div class="post-excerpt">{{ post.content }}</div>
        <div class="post-tags">
          <span v-for="tag in post.tags" :key="tag" class="tag">{{ tag }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getPosts, getTags } from '../api'

const route = useRoute()
const router = useRouter()

const posts = ref([])
const tags = ref([])
const activeTag = ref(null)
const loading = ref(true)
const dropdownOpen = ref(false)
const tagSearch = ref('')
const selectRef = ref(null)
const searchInput = ref(null)

const searchQuery = computed(() => route.query.q || '')

const filteredTags = computed(() => {
  const q = tagSearch.value.toLowerCase()
  if (!q) return tags.value
  return tags.value.filter((t) => t.toLowerCase().includes(q))
})

async function load() {
  loading.value = true
  posts.value = await getPosts({ tag: activeTag.value, q: searchQuery.value || undefined })
  loading.value = false
}

function selectTag(t) {
  activeTag.value = activeTag.value === t ? null : t
  dropdownOpen.value = false
  tagSearch.value = ''
}

function clearTag() {
  activeTag.value = null
}

function clearSearch() {
  router.push('/')
}

function handleClickOutside(e) {
  if (selectRef.value && !selectRef.value.contains(e.target)) {
    dropdownOpen.value = false
    tagSearch.value = ''
  }
}

onMounted(async () => {
  tags.value = await getTags()
  await load()
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})

watch([activeTag, () => route.query.q], load)

watch(dropdownOpen, (open) => {
  if (open) {
    nextTick(() => searchInput.value?.focus())
  }
})
</script>

<style scoped>
.search-state {
  padding: 14px 18px;
  background: #eef2ff;
  border-radius: 10px;
  font-size: 14px;
  color: var(--primary);
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.clear-link {
  color: var(--text-muted);
  font-size: 13px;
  text-decoration: underline;
}

/* Tag select */
.tag-select {
  position: relative;
  min-width: 180px;
}

.tag-select-input {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 10px;
  border: 1.5px solid #c7d2fe;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  min-height: 34px;
  transition: border-color 0.2s;
}

.tag-select-input:hover {
  border-color: var(--primary);
}

.tag-select-placeholder {
  color: var(--text-muted);
  font-size: 13px;
}

.tag-select-arrow {
  margin-left: auto;
  color: var(--text-muted);
  transition: transform 0.2s;
}

.tag-select-arrow.open {
  transform: rotate(180deg);
}

.tag-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  min-width: 200px;
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  z-index: 999;
  overflow: hidden;
}

.tag-dropdown-search {
  border: none;
  border-bottom: 1px solid var(--border);
  border-radius: 0;
  padding: 10px 14px;
  font-size: 14px;
}

.tag-dropdown-search:focus {
  box-shadow: none;
}

.tag-dropdown-list {
  max-height: 220px;
  overflow-y: auto;
}

.tag-dropdown-item {
  padding: 8px 14px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
}

.tag-dropdown-item:hover {
  background: #f1f5f9;
}

.tag-dropdown-item.active {
  background: #eef2ff;
  color: var(--primary);
  font-weight: 500;
}

.tag-dropdown-empty {
  padding: 16px 14px;
  text-align: center;
  color: var(--text-muted);
  font-size: 13px;
}
</style>
