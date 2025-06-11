<template>
  <div>
    <!-- Header Section -->
    <header>
      <NavBar />
    </header>

    <!-- Hero Section -->
    <section>
      <HeroPage />
    </section>

    <!-- Features Section -->
    <section>
      <RouterView />
    </section>

    <!-- Footer Section -->
    <footer >
      <div class="flex ">
        <div @click="navigateHome" class="w-40">
          <i-mdi-controller-classic class="w-12 h-12 text-black" />
        </div>

        <div class="flex justify-around items-start w-3/5">
          <div class="flex flex-col gap-8">
            <h2 class="font-bold font-header text-xl capitalize">helpful links</h2>
            <ul class="flex flex-col gap-4">
              <li>home page</li>
              <li>feelings hub</li>
              <li>Contact us</li>
              <li>support center</li>
              <li>feedback form</li>
            </ul>
          </div>
          <div class="flex flex-col gap-8">

            <h2 class="font-bold font-header text-xl capitalize">stay connected</h2>
            <ul class="flex flex-col gap-4">
              <li>social media</li>
              <li>email updates</li>
              <li>community blog</li>
              <li>resources center</li>
              <li>help articles</li>
            </ul>
          </div>
          <div class="flex flex-col gap-8">

            <h2 class="font-bold font-header text-xl capitalize">newsletter signup</h2>
            <ul class="flex flex-col gap-4">
              <li>join now</li>
              <li>get updates</li>
              <li>latest news</li>
              <li>special offers</li>
              <li>event alerts</li>
            </ul>
          </div>
        </div>

        <div class="flex flex-col gap-4">
          <h2 class="font-bold font-header text-xl capitalize mb-4">subscribe</h2>
          <p>join our newsletter to stay updated on features and releases</p>
          <div class="flex gap-4">
            <input type="text" class="border p-4 placeholder:font-semibold" placeholder="enter your email"/>
            <button class="border capitalize p-4 text-center">subscribe</button>
          </div>
          <p>by subscribing you agree to our privacy policy and consent to receive updates</p>
        </div>
      </div>

      <div class="border-t flex justify-between items-center px-16 py-4">

        <div class="flex gap-4">
          <p>&copy; 2024 OPENCFFS. All Rights Reserved.</p>
          <p class="underline">privacy policy</p>
          <p class="underline">terms and conditions</p>
          <p class="underline">cookies settings</p>
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
    <div v-if="showBadge" class="thank-you-modal">
      <div class="modal-content">
        <h2>Thank You!</h2>
        <p>You've made a difference today!</p>
        <button @click="closeBadge">Close</button>
      </div>
    </div>
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
