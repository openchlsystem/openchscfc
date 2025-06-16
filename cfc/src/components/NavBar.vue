<template>
  <nav>
    <div class="flex justify-between items-center px-16 py-4">
      <!-- Home Icon -->
      <div @click="navigateHome" class="cursor-pointer">
        <i-mdi-controller-classic class="w-12 h-12 text-black" />
      </div>

      <!-- Navigation Links -->
      <div class="flex justify-between items-center gap-4 capitalize">
        <router-link to="/" class="p-2 cursor-pointer">home page</router-link>
        <router-link to="/safe-sharing" class="p-2">feelings hub</router-link>
        <router-link to="/child-help" class="p-2">contact us</router-link>
        <router-link to="/interactive-games" class="p-2">games</router-link>
        <div class="flex items-center p-2">
          <router-link to="/about" class="mr-1">leaderboard</router-link>
          <i-mdi-chevron-down class="w-6 h-6 text-black" />
        </div>
        <button class="border py-2 px-4 capitalize">send</button>
        <button class="border py-2 px-4 capitalize bg-black text-white">submit</button>
      </div>
    </div>
  </nav>
</template>


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
