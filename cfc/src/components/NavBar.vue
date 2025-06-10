<template>
  <nav>
    <div class="flex justify-between items-center px-16 py-4">
      <!-- Home Icon -->
      <div @click="navigateHome" class="cursor-pointer">
        <i-mdi-controller-classic  class="w-12 h-12 text-black" />
      </div>

      <!-- Navigation Links with <div> and <p> -->
      <div class="flex justify-between items-center gap-4  capitalize">
        <p class="p-2 cursor-pointer">home page</p>
        <p class="p-2"><a href="#features">feelings hub</a></p>
        <p class="p-2"><a href="#about">About</a></p>
        <p class="p-2"><a href="#contact">Contact us</a></p>
        <div class="flex items-center p-2">
            <p ><a href="#support">leaderboard</a></p>
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
