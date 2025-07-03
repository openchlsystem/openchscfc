<template>
  <nav class="fixed top-4 left-4 right-4 z-50 bg-white shadow-lg rounded-3xl">
    <div class="flex justify-between items-center px-6 py-2md:px-16">
      <!-- Logo Image -->
      <div @click="navigateHome" class="cursor-pointer">
        <img :src="logo" alt="Logo" class="w-16 h-auto" />
      </div>

      <!-- Hamburger Icon (Mobile Only) -->
      <div class="md:hidden cursor-pointer" @click="isMenuOpen = !isMenuOpen">
        <i-mdi-menu class="w-8 h-8 text-black" />
      </div>

      <!-- Desktop Navigation -->
      <div class="hidden md:flex justify-between items-center gap-4 capitalize">
        <router-link to="/" class="p-2 cursor-pointer font-text">home page</router-link>
        <router-link to="/safe-sharing" class="p-2 font-text">feelings hub</router-link>
        <router-link to="/child-help" class="p-2 font-text">contact us</router-link>
        <router-link to="/interactive-games" class="p-2 font-text">games</router-link>
        <router-link to="/safe-sharing#draw-section" class="py-2 px-4 capitalize font-header bg-button rounded-2xl text-white hover:text-purple-900 hover:bg-purple-100 transition">draw</router-link>
        <router-link to="/child-help#chat-section" class="py-2 px-4 capitalize font-header bg-button rounded-2xl text-white hover:text-purple-900 hover:bg-purple-100 transition">chat</router-link>
      </div>
    </div>

    <!-- Mobile Menu (Dropdown) -->
    <div v-if="isMenuOpen" class="flex flex-col gap-4 px-6 pb-4 md:hidden">
      <router-link to="/" class="p-2 border-b border-black rounded-none font-text"> home page </router-link>
      <router-link to="/safe-sharing" class="p-2 border-b border-black rounded-none font-text">feelings hub</router-link>
      <router-link to="/child-help" class="p-2 border-b border-black rounded-none font-text">contact us</router-link>
      <router-link to="/interactive-games" class="p-2 border-b border-black rounded-none font-text">games</router-link>
      <router-link to="/safe-sharing#draw-section" class="border py-2 px-4 capitalize bg-button rounded-2xl text-white hover:text-purple-900 hover:bg-purple-100 transition text-center">draw</router-link>
      <router-link to="/child-help#chat-section" class="border py-2 px-4 capitalize bg-button rounded-2xl text-white hover:text-purple-900 hover:bg-purple-100 transition text-center">chat</router-link>
    </div>
  </nav>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import logo from '@/assets/Icons/logo-1.png' // ✅ fixed path: 'assets', not 'asset'

export default {
  setup() {
    const isMenuOpen = ref(false)
    const router = useRouter()

    const toggleMenu = () => {
      isMenuOpen.value = !isMenuOpen.value
    }

    const navigateHome = () => {
      router.push('/')
    }

    const navigateBack = () => {
      router.back()
    }

    return {
      logo, // ✅ expose logo to template
      isMenuOpen,
      toggleMenu,
      navigateHome,
      navigateBack,
    }
  },
}
</script>
