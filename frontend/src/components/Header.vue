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

const themeStore = useThemeStore()
</script>

<style scoped>
.header {
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--glass-border);
  padding: 16px 0;
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
  font-size: 18px;
  transition: opacity 0.2s;
}

.logo:hover {
  opacity: 0.8;
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
  gap: 8px;
  flex: 1;
}

.nav-link {
  padding: 8px 16px;
  border-radius: 8px;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 15px;
  transition: all 0.2s;
  position: relative;
}

.nav-link:hover {
  color: var(--text-primary);
  background: var(--code-bg);
}

.nav-link.router-link-active {
  color: var(--accent);
  background: var(--code-bg);
}

.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.theme-toggle:hover {
  background: var(--code-bg);
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .header-content {
    gap: 16px;
  }

  .logo-text {
    display: none;
  }

  .nav {
    gap: 4px;
  }

  .nav-link {
    padding: 8px 12px;
    font-size: 14px;
  }

  .theme-toggle {
    width: 36px;
    height: 36px;
  }
}
</style>
