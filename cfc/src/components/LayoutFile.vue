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
    <footer class="flex flex-col gap-20">
      <div class="flex justify-around gap-32">
        <div class="flex items-start justify-between gap-32">
          <div @click="navigateHome" class="w-1/4">
            <i-mdi-controller-classic class="w-20 h-16 text-black" />
          </div>

          <div class="flex flex-col gap-4 w-1/4">
            <h2 class="font-bold font-header text-xl capitalize">Helpful Links</h2>
            <ul class="flex flex-col gap-4">
              <li>Home Page</li>
              <li>Feelings Hub</li>
              <li>Contact Us</li>
              <li>Support Center</li>
              <li>Feedback Form</li>
            </ul>
          </div>

          <div class="flex flex-col gap-4 w-1/4">
            <h2 class="font-bold font-header text-xl capitalize">Stay Connected</h2>
            <ul class="flex flex-col gap-4">
              <li>Social Media</li>
              <li>Email Updates</li>
              <li>Community Blog</li>
              <li>Resource Center</li>
              <li>Help Articles</li>
            </ul>
          </div>

          <div class="flex flex-col gap-4 w-1/4">
            <h2 class="font-bold font-header text-xl capitalize">Newsletter Signup</h2>
            <ul class="flex flex-col gap-4">
              <li>Join Now</li>
              <li>Get Updates</li>
              <li>Latest News</li>
              <li>Special Offers</li>
              <li>Event Alerts</li>
            </ul>
          </div>
        </div>

        <div class="flex flex-col gap-6 w-[400px]">
          <h2 class="font-semibold font-header text-xl capitalize">Subscribe</h2>
          <p>Join our newsletter to stay updated on features and releases.</p>
          <div class="flex gap-4 pr-4">
            <input
              type="text"
              class="border p-4 placeholder:font-semibold w-2/3"
              placeholder="enter your email"
            />
            <button class="border capitalize p-4 text-center w-1/3">Subscribe</button>
          </div>
          <p>By subscribing, you agree to our Privacy Policy and consent to receive updates.</p>
        </div>
      </div>

      <div class="border-t flex justify-between items-center px-16 py-4">
        <div class="flex gap-4">
          <p>© 2024 CHS. All rights reserved.</p>
          <p class="underline">Privacy Policy</p>
          <p class="underline">Terms of Service</p>
          <p class="underline">Cookies Settings</p>
        </div>

        <div class="flex gap-4">
          <i-mdi-facebook class="w-8 h-8 text-black" />
          <i-mdi-instagram class="w-8 h-8 text-black" />
          <i-mdi-twitter class="w-8 h-8 text-black" />
          <i-mdi-linkedin class="w-8 h-8 text-black" />
          <i-mdi-youtube class="w-8 h-8 text-black" />
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
