<template>
  <div class="games">
    <div class="container">
      <div class="page-header">
        <div>
          <h1 class="page-title">Игровая библиотека</h1>
          <p class="page-description">Управляйте своей коллекцией игр Steam</p>
        </div>
        <button @click="handleImport" :disabled="loading || !userId" class="btn btn-primary">
          <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 3V13M10 13L6 9M10 13L14 9" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <path d="M3 17H17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
          <span v-if="!loading">Импортировать игры</span>
          <span v-else>Импорт...</span>
        </button>
      </div>

      <div v-if="error" class="error-banner">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M10 6V10M10 14V14.5" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        {{ error }}
      </div>

      <div v-if="importSuccess" class="success-banner">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="2"/>
          <path d="M6 10L9 13L14 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        {{ importSuccess }}
      </div>

      <div v-if="(loading || sessionLoading) && games.length === 0" class="loading-state">
        <div class="spinner"></div>
        <p>Загрузка игр...</p>
      </div>

      <div v-else-if="games.length === 0" class="empty-state">
        <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
          <rect x="8" y="20" width="48" height="32" rx="4" stroke="currentColor" stroke-width="2"/>
          <circle cx="20" cy="36" r="4" stroke="currentColor" stroke-width="2"/>
          <circle cx="44" cy="36" r="4" stroke="currentColor" stroke-width="2"/>
          <path d="M28 30H36M28 42H36" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
        </svg>
        <h3>{{ userId ? 'Нет игр' : 'Войдите через Steam' }}</h3>
        <p>{{ userId ? 'Импортируйте игры из своей Steam библиотеки' : 'После входа здесь появится ваша библиотека' }}</p>
        <RouterLink v-if="!userId" to="/" class="btn btn-primary">Войти</RouterLink>
      </div>

      <div v-else class="games-grid">
        <div v-for="game in sortedGames" :key="game.id" class="game-card">
          <div class="game-icon">
            <img v-if="game.img_icon_url"
                 :src="`https://media.steampowered.com/steamcommunity/public/images/apps/${game.app_id}/${game.img_icon_url}.jpg`"
                 :alt="game.name"
                 @error="handleImageError">
            <div v-else class="game-icon-placeholder">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <rect x="4" y="4" width="16" height="16" rx="2" stroke="currentColor" stroke-width="2"/>
                <path d="M8 12L12 16L16 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
          </div>

          <div class="game-info">
            <h3 class="game-name">{{ game.name }}</h3>
            <div class="game-stats">
              <div class="stat">
                <span class="stat-label">Всего:</span>
                <span class="stat-value">{{ formatPlaytime(game.playtime_forever) }}</span>
              </div>
              <div v-if="game.playtime_2weeks" class="stat">
                <span class="stat-label">2 недели:</span>
                <span class="stat-value">{{ formatPlaytime(game.playtime_2weeks) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const userId = computed(() => userStore.currentUser?.id)
const sessionLoading = ref(true)
const importSuccess = ref<string | null>(null)

const games = computed(() => userStore.games)
const loading = computed(() => userStore.loading)
const error = computed(() => userStore.error)

const sortedGames = computed(() => {
  return [...games.value].sort((a, b) => b.playtime_forever - a.playtime_forever)
})

const handleImport = async () => {
  if (!userId.value) return

  try {
    importSuccess.value = null
    const result = await userStore.importGames(userId.value)
    importSuccess.value = `Импортировано ${result.games_added} новых игр, обновлено ${result.games_updated}`

    setTimeout(() => {
      importSuccess.value = null
    }, 5000)

    await userStore.fetchGames(userId.value)
  } catch (err) {
    console.error('Import failed:', err)
  }
}

const formatPlaytime = (minutes: number) => {
  if (minutes < 60) return `${minutes}м`
  const hours = Math.floor(minutes / 60)
  if (hours < 100) return `${hours}ч`
  return `${hours}ч`
}

const handleImageError = (e: Event) => {
  const target = e.target as HTMLImageElement
  target.style.display = 'none'
}

onMounted(async () => {
  try {
    const user = await userStore.loadCurrentUser()
    if (user) await userStore.fetchGames(user.id)
  } catch (err) {
    console.error('Failed to load games:', err)
  } finally {
    sessionLoading.value = false
  }
})
</script>

<style scoped>
.games {
  min-height: calc(100vh - 200px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  gap: 24px;
}

.page-title {
  font-size: 40px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  letter-spacing: -0.02em;
}

.page-description {
  font-size: 16px;
  color: var(--text-secondary);
  font-weight: 500;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  white-space: nowrap;
  cursor: pointer;
}

.btn-primary {
  background: var(--accent);
  color: #0B0E14;
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(56, 189, 248, 0.35);
}

.btn-primary:active:not(:disabled) {
  transform: translateY(0);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-banner,
.success-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border-radius: 8px;
  margin-bottom: 24px;
  font-size: 14px;
  font-weight: 500;
}

.error-banner {
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: var(--error);
}

.success-banner {
  background: rgba(79, 209, 197, 0.08);
  border: 1px solid rgba(79, 209, 197, 0.2);
  color: var(--success);
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 24px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--glass-border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p,
.empty-state p {
  color: var(--text-secondary);
  font-size: 15px;
  margin-top: 12px;
  font-weight: 500;
}

.empty-state svg {
  color: var(--text-tertiary);
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-state h3 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 12px;
}

.game-card {
  display: flex;
  gap: 14px;
  padding: 14px;
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  border-radius: 10px;
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(12px);
}

.game-card:hover {
  background: var(--glass-hover);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border-color: var(--text-tertiary);
}

.game-icon {
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 6px;
  overflow: hidden;
  background: var(--code-bg);
}

.game-icon img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.game-icon-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
}

.game-info {
  flex: 1;
  min-width: 0;
}

.game-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.game-stats {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.stat {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
}

.stat-label {
  color: var(--text-tertiary);
  font-weight: 500;
}

.stat-value {
  color: var(--text-secondary);
  font-family: 'JetBrains Mono', monospace;
  font-weight: 600;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-title {
    font-size: 32px;
  }

  .btn {
    width: 100%;
    justify-content: center;
  }

  .games-grid {
    grid-template-columns: 1fr;
  }
}
</style>
