<template>
  <div class="py-20 px-6 sm:px-10 md:px-16 flex flex-col gap-20">
    <!-- Header Section -->
    <div class="flex flex-col lg:flex-row gap-8 lg:justify-between lg:items-start">
      <!-- Heading -->
      <h1 class="font-extrabold font-header text-4xl sm:text-5xl lg:w-3/7 text-center lg:text-left">
        Welcome to Your Safe Space for Feelings
      </h1>

      <!-- Text and Buttons -->
      <div class="flex flex-col gap-6 lg:gap-8 lg:w-3/7 text-center lg:text-left">
        <p class="text-base sm:text-lg">
          Here, children can explore their emotions in a fun and engaging way. Our vibrant interface
          and friendly design make it easy to express feelings and connect with others.
        </p>
        <div
          class="flex flex-col sm:flex-row sm:justify-center lg:justify-start items-center gap-4"
        >
          <router-link
            to="/child-help#chat-section"
            class="capitalize px-6 py-2 bg-black text-white w-full rounded-lg sm:w-auto text-center"
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
        src="https://imgs.search.brave.com/a4ZTHrZwdH2-zrSmfFM1xODUI-_3QOACAWowJLbsExo/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvOTUw/NjA1MDQ2L3Bob3Rv/L211bHRpZXRobmlj/LWNoaWxkcmVuLWlu/LWEtY2lyY2xlLmpw/Zz9zPTYxMng2MTIm/dz0wJms9MjAmYz1I/YXd6V0g4ZkJ6c0pT/dXp2aXV1UzNpUmhS/UEF3RVcyUE9RVExR/M0x6VWZZPQ"
        alt="Happy children illustration"
        class="w-full h-auto max-h-[500px] rounded-3xl object-cover"
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
