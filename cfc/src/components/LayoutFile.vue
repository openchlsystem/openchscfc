<template>
  <div>
    <!-- Header Section -->
    <header>
      <NavBar />
    </header>

    <!-- Hero Section -->
    <section v-if="currentRoute === '/'">
      <HeroPage />
    </section>

    <!-- Features Section -->
    <section>
      <RouterView />
    </section>

    <!-- Footer Section -->
    <footer class="flex flex-col gap-16 py-16 px-6 md:px-16 bg-white">
      <!-- Top Content Section -->
      <div class="flex flex-col lg:flex-row gap-12 justify-between">
        <!-- Link Columns (no wrapping) -->
        <div
          class="flex flex-col md:flex-row md:justify-between flex-nowrap gap-12 flex-grow overflow-x-auto"
        >
          <!-- Logo -->
          <div @click="navigateHome" class="w-full md:w-auto flex justify-start cursor-pointer">
            <img :src="logo" alt="CHS Logo" class="w-28 h-auto object-contain" />
          </div>

          <!-- Column 1 -->
          <div class="flex flex-col gap-4 min-w-[150px]">
            <h2 class="font-bold font-header text-lg capitalize">Helpful Links</h2>
            <ul class="flex flex-col gap-2 text-sm font-text">
              <li>Home Page</li>
              <li>Feelings Hub</li>
              <li>Contact Us</li>
              <li>Support Center</li>
              <li>Feedback Form</li>
            </ul>
          </div>

          <!-- Column 2 -->
          <div class="flex flex-col gap-4 min-w-[150px]">
            <h2 class="font-bold font-header text-lg capitalize">Stay Connected</h2>
            <ul class="flex flex-col gap-2 text-sm font-text">
              <li>Social Media</li>
              <li>Email Updates</li>
              <li>Community Blog</li>
              <li>Resource Center</li>
              <li>Help Articles</li>
            </ul>
          </div>

          <!-- Column 3 -->
          <div class="flex flex-col gap-4 min-w-[150px]">
            <h2 class="font-bold font-header text-lg capitalize">Newsletter Signup</h2>
            <ul class="flex flex-col gap-2 text-sm font-text">
              <li>Join Now</li>
              <li>Get Updates</li>
              <li>Latest News</li>
              <li>Special Offers</li>
              <li>Event Alerts</li>
            </ul>
          </div>
        </div>

        <!-- Subscribe Form (stacks below on smaller screens) -->
        
      </div>

      <!-- Bottom Bar -->
      <div
        class="border-t pt-6 flex flex-col md:flex-row justify-between items-center text-sm gap-4"
      >
        <div class="flex flex-wrap justify-center md:justify-start gap-4 text-center">
          <p>© 2024 CHS. All rights reserved.</p>
          <p class="underline cursor-pointer">Privacy Policy</p>
          <p class="underline cursor-pointer">Terms of Service</p>
          <p class="underline cursor-pointer">Cookies Settings</p>
        </div>
        <div class="flex gap-4 justify-center">
          <i-mdi-facebook class="w-6 h-6 text-black" />
          <i-mdi-instagram class="w-6 h-6 text-black" />
          <i-mdi-twitter class="w-6 h-6 text-black" />
          <i-mdi-linkedin class="w-6 h-6 text-black" />
          <i-mdi-youtube class="w-6 h-6 text-black" />
        </div>
      </div>
    </footer>

    <!-- Thank You Badge Modal -->
    <!-- <div v-if="showBadge" class="thank-you-modal">
      <div class="modal-content">
        <h2>Thank You!</h2>
        <p>You've made a difference today!</p>
        <button @click="closeBadge">Close</button>
      </div>
    </div>
     -->
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ChildFriendlyCard from '@/components/ChildFriendlyCard.vue'
import NavBar from './NavBar.vue'
import HeroPage from './HeroPage.vue'
import logo from '@/assets/Icons/logo-1.png'

export default {
  components: {
    ChildFriendlyCard,
    NavBar,
    HeroPage,
  },
  setup() {
    const router = useRouter()
    const showBadge = ref(false)
    const route = useRoute()
    const currentRoute = ref(route.path)
    watch(route, () => {
      currentRoute.value = route.path
    })

    const closeBadge = () => {
      showBadge.value = false
    }

    return {
      showBadge,
      closeBadge,
      currentRoute,
      logo,
    }
  },
}
</script>

<style scoped>
.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-top: 2rem;
  justify-items: center;
  padding: 0 1rem;
}

@media (max-width: 768px) {
  .features-grid {
    grid-template-columns: 1fr;
    gap: 1.25rem;
  }
}
</style>
