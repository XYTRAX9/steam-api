<template>
  <div id="app">
    <Header />
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import Header from '@/components/Header.vue'
import { useThemeStore } from '@/stores/theme'
import { useUserStore } from '@/stores/user'

const themeStore = useThemeStore()
const userStore = useUserStore()

onMounted(() => {
  themeStore.initTheme()
  userStore.loadCurrentUser().catch(() => {})
})
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
  padding: 32px 0;
}

@media (max-width: 768px) {
  main {
    padding: 24px 0;
  }
}
</style>
