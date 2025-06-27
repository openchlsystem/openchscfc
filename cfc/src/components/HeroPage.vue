<template>
  <div class="pb-20 pt-44 px-6 sm:px-10 md:px-16 flex flex-col gap-20 bg-background">
    <!-- Header Section -->
    <div class="flex flex-col lg:flex-row gap-8 lg:justify-between lg:items-start">
      <!-- Heading -->
      <h1 class="font-extrabold font-header text-4xl sm:text-5xl lg:w-3/7 text-center lg:text-left">
        Welcome to Your Safe Space for Feelings
      </h1>

      <!-- Text and Buttons -->
      <div class="flex flex-col gap-6 lg:gap-8 lg:w-3/7 text-center lg:text-left">
        <p class="text-base sm:text-lg font-text">
          Here, children can explore their emotions in a fun and engaging way. Our vibrant interface
          and friendly design make it easy to express feelings and connect with others.
        </p>
        <div
          class="flex flex-col sm:flex-row sm:justify-center lg:justify-start items-center gap-4"
        >
          <router-link
            to="/child-help#chat-section"
            class="capitalize px-6 py-2 bg-button font-header text-white w-full rounded-lg sm:w-auto text-center hover:text-purple-900 hover:bg-purple-100 transition"
          >
            Talk to us
          </router-link>
          <!-- <button class="capitalize px-6 py-2 border w-full sm:w-auto">learn more</button> -->
        </div>
      </div>
    </div>

    <!-- Image Section -->
    <div>
      <img
        src="../assets/images/hero.jpeg"
        alt="Happy children illustration"
        class="w-full h-auto max-h-[500px] rounded-3xl object-cover shadow-2xl"
      />
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()
    const navigateToStart = () => {
      window.location.replace('/safe-sharing')
    }

    return {
      navigateToStart,
    }
  },
}
</script>
