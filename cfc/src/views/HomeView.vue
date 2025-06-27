<template>
  <div class="flex flex-col gap-20 pb-28 justify-center items-center px-4 md:px-16 bg-background">
    <!-- Header Section -->
    <div class="flex flex-col gap-4 justify-center items-center text-center">
      <p class="font-semibold font-header">Explore</p>
      <h2 class="font-bold font-header text-3xl md:text-5xl">Navigate Your Feelings with Ease</h2>
      <p class="text-gray-700 text-lg font-text">
        Our platform offers quick access to essential features. Dive into the Feelings Hub or reach
        out through Contact Us.
      </p>
    </div>

    <!-- Features Section -->
    <div class="flex flex-col md:flex-row gap-6 md:gap-12 w-full ">
      <div
        v-for="(feature, index) in features"
        :key="feature.title"
        :class="[
          'flex flex-col justify-center items-center rounded-2xl px-6 py-8 w-full bg-white md:w-1/3  text-center shadow-lg transition-transform duration-300 hover:scale-105 hover:shadow-xl'
          
        ]"
      >
       <h2 class="w-full text-center font-bold font-header text-purple-900 text-2xl md:text-3xl bg-cardhead rounded-t-2xl py-4 px-2">
  {{ feature.title }}
</h2>
        <p class="font-text max-w-xs mt-2 ">{{ feature.description }}</p>
        <button
          class="rounded-lg px-4 py-2 mt-4 bg-button text-white font-header  hover:text-purple-900 hover:bg-purple-100 transition"
          @click="feature.action"
        >
          {{ feature.buttonText }}
        </button>
      </div>
    </div>

    <!-- Action Buttons -->
    <div class="flex flex-col sm:flex-row gap-4 mt-4">
      <!-- Draw Button -->
      <router-link to="/safe-sharing#draw-section">
        <button class="px-6 py-2 w-full sm:w-auto bg-button rounded-xl text-white font-header hover:text-purple-900 hover:bg-purple-100 transition">Draw</button>
      </router-link>

      <!-- Chat Button -->
      <router-link to="/child-help#chat-section">
        <div class="flex items-center justify-center gap-2 px-6 py-2 w-full sm:w-auto hover:text-button transition">
          <span class="font-header">Chat</span>
          <i-mdi-chevron-right class="w-5 h-5 text-black" />
        </div>
      </router-link>
    </div>
  </div>
</template>

<script>
// import ChildFriendlyCard from "@/components/ChildFriendlyCard.vue";

export default {
  components: {
    // ChildFriendlyCard,
  },
  data() {
    return {
      showBadge: false,
      features: [
        {
          title: 'Friendly Support',
          description: 'Reach out to trained professionals for guidance and help.',
          buttonText: 'Learn More',
          action: this.navigateToHelp,
        },
        {
          title: 'Interactive Games',
          description: 'Engage with activities that teach and entertain.',
          buttonText: 'Play Games',
          action: this.navigateToGames,
        },
        {
          title: 'Safe Sharing',
          description: 'Share your story in a secure and non-judgmental environment.',
          buttonText: 'Share Now',
          action: this.navigateToSafeSharing,
        },
      ],
    }
  },
  methods: {
    navigateToStart() {
      this.$router.push('/start')
    },
    navigateToGames() {
      this.$router.push('/interactive-games')
    },
    navigateToHelp() {
      this.$router.push('/child-help')
    },
    navigateToSafeSharing() {
      this.$router.push('/safe-sharing')
    },
    closeBadge() {
      this.showBadge = false
    },
  },
}
</script>

<style scoped></style>
