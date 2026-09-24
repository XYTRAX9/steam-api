<template>
  <header class="header glass">
    <div class="container">
      <div class="header-content">
        <RouterLink to="/" class="logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="currentColor" opacity="0.1"/>
            <path d="M16 8L24 12V20L16 24L8 20V12L16 8Z" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>
            <circle cx="16" cy="16" r="3" fill="currentColor"/>
          </svg>
          <span class="logo-text">Steam Integration</span>
        </RouterLink>

        <nav class="nav">
          <RouterLink to="/" class="nav-link">Home</RouterLink>
          <RouterLink to="/games" class="nav-link">Games</RouterLink>
          <RouterLink to="/status" class="nav-link">Status</RouterLink>
        </nav>

        <div v-if="userStore.currentUser" class="account">
          <span class="account-name">{{ userStore.currentUser.persona_name }}</span>
          <span v-if="logoutError" class="logout-error">Ошибка выхода</span>
          <button class="sign-out" @click="handleLogout">Выйти</button>
        </div>

        <button @click="themeStore.toggleTheme" class="theme-toggle" aria-label="Toggle theme">
          <svg v-if="themeStore.theme === 'light'" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M10 3V1M10 19V17M17 10H19M1 10H3M15.657 4.343L17.071 2.929M2.929 17.071L4.343 15.657M15.657 15.657L17.071 17.071M2.929 2.929L4.343 4.343"
                  stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <circle cx="10" cy="10" r="4" stroke="currentColor" stroke-width="2"/>
          </svg>
          <svg v-else width="20" height="20" viewBox="0 0 20 20" fill="none">
            <path d="M17 10.5C16.4 13.5 13.5 16 10 16C6.5 16 3.5 13.5 3 10.5C2.5 7.5 4.5 4.5 7.5 3.5C6.5 4.5 6 6 6 7.5C6 10.5 8.5 13 11.5 13C13 13 14.5 12.5 15.5 11.5C16.5 12.5 17 14 17 10.5Z"
                  fill="currentColor"/>
          </svg>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useThemeStore } from '@/stores/theme'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { ref } from 'vue'

const themeStore = useThemeStore()
const userStore = useUserStore()
const router = useRouter()
const logoutError = ref(false)

const handleLogout = async () => {
  try {
    logoutError.value = false
    await userStore.logout()
    router.push('/')
  } catch {
    logoutError.value = true
  }
}
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--glass-border);
  padding: 12px 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 32px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 16px;
  transition: opacity 0.15s;
  letter-spacing: -0.01em;
}

.logo:hover {
  opacity: 0.7;
}

.logo svg {
  color: var(--accent);
}

.logo-text {
  white-space: nowrap;
}

.nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.nav-link {
  padding: 8px 14px;
  border-radius: 6px;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 14px;
  transition: all 0.15s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--code-bg);
}

.nav-link.router-link-active {
  color: var(--accent);
  background: rgba(56, 189, 248, 0.08);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: var(--text-secondary);
  transition: all 0.15s;
  cursor: pointer;
}

.theme-toggle:hover {
  background: var(--code-bg);
  color: var(--text-primary);
}

.theme-toggle:active {
  transform: scale(0.95);
}

.account {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
}

.account-name {
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-secondary);
  font-size: 13px;
}

.sign-out {
  border: 0;
  background: transparent;
  color: var(--text-secondary);
  font: inherit;
  font-size: 13px;
  cursor: pointer;
}

.sign-out:hover {
  color: var(--text-primary);
}

.logout-error {
  color: var(--error);
  font-size: 12px;
  white-space: nowrap;
}

@media (max-width: 768px) {
  .header {
    padding: 10px 0;
  }

  .header-content {
    flex-wrap: wrap;
    gap: 8px 12px;
  }

  .logo {
    margin-right: auto;
  }

  .nav {
    order: 3;
    flex-basis: 100%;
    justify-content: space-between;
  }

  .logo-text {
    display: none;
  }

  .logo {
    font-size: 15px;
  }

  .nav {
    gap: 2px;
  }

  .nav-link {
    padding: 7px 12px;
    font-size: 13px;
  }

  .theme-toggle {
    width: 34px;
    height: 34px;
  }

  .account-name {
    display: none;
  }
}
</style>
