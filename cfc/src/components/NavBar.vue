<template>
  <nav>
    <div class="flex justify-between items-center px-6 py-4 md:px-16">
      <!-- Home Icon -->
      <div @click="navigateHome" class="cursor-pointer">
        <i-mdi-controller-classic class="w-10 h-10 text-black" />
      </div>

      <!-- Hamburger Icon (Mobile Only) -->
      <div class="md:hidden cursor-pointer" @click="isMenuOpen = !isMenuOpen">
        <i-mdi-menu class="w-8 h-8 text-black" />
      </div>

      <!-- Desktop Navigation -->
      <div class="hidden md:flex justify-between items-center gap-4 capitalize">
        <router-link to="/" class="p-2 cursor-pointer">home page</router-link>
        <router-link to="/safe-sharing" class="p-2">feelings hub</router-link>
        <router-link to="/child-help" class="p-2">contact us</router-link>
        <router-link to="/interactive-games" class="p-2">games</router-link>
        <button class="border py-2 px-4 capitalize">send</button>
        <button class="border py-2 px-4 capitalize bg-black text-white">submit</button>
      </div>
    </div>

    <!-- Mobile Menu (Dropdown) -->
    <div v-if="isMenuOpen" class="flex flex-col gap-4 px-6 pb-4 md:hidden">
      <router-link to="/" class="p-2 border-b rounded-r-md">home page</router-link>
      <router-link to="/safe-sharing" class="p-2 border-b rounded-r-md">feelings hub</router-link>
      <router-link to="/child-help" class="p-2 border-b rounded-r-md">contact us</router-link>
      <router-link to="/interactive-games" class="p-2 border-b rounded-r-md">games</router-link>
      <button class="border py-2 px-4 capitalize">send</button>
      <button class="border py-2 px-4 capitalize bg-black text-white">submit</button>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'

const isMenuOpen = ref(false)

const navigateHome = () => {
  // handle home navigation logic if needed
}
</script>



<script>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { Icon } from "@iconify/vue";

export default {
  components: { Icon },
  setup() {
    const isMenuOpen = ref(false);
    const router = useRouter();

    const toggleMenu = () => {
      isMenuOpen.value = !isMenuOpen.value;
    };

    const navigateHome = () => {
      router.push("/");
    };

    const navigateBack = () => {
      router.back();
    };

    return {
      isMenuOpen,
      toggleMenu,
      navigateHome,
      navigateBack,
    };
  },
};
</script>
