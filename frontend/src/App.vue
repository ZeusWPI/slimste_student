<script setup lang="ts">
import { onMounted } from 'vue'
import { useAuth } from './composables/useAuth'
import { initializeCsrf } from './utils/csrf'

const { checkAuth } = useAuth()

onMounted(async () => {
  await initializeCsrf()
  await checkAuth()
})
</script>

<template>
  <div id="app">
    <router-view />
  </div>
</template>

<style scoped>
#app {
  min-height: 100vh;
}
</style>
