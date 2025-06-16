<template>
  <div class="flex flex-col gap-20 mb-28 justify-center items-center">
    <div class="flex flex-col gap-4 justify-center items-center">
      <p class="font-semibold font-header">Explore</p>
      <h2 class="font-bold font-header text-5xl">Navigate Your Feelings with Ease</h2>
      <p class="text-center text-gray-700 text-lg">
        Our platform offers quick access to essential features. Dive into the Feelings Hub or reach
        out through Contact Us.
      </p>
    </div>

    <div class="flex gap-12">
      <div
        v-for="(feature, index) in features"
        :key="feature.title"
        :class="[
          'flex flex-col justify-center items-center  rounded-lg px-4 py-12 w-1/3 h-60',
          index % 2 === 0 ? 'bg-white' : 'bg-slate-300',
        ]"
      >
        <h2 class="font-bold font-header text-center text-3xl">{{ feature.title }}</h2>
        <p class="text-center text-gray-700 max-w-xs mt-2">{{ feature.description }}</p>
        <button
          class="rounded-lg px-4 py-2 mt-4 bg-white hover:underline"
          :class="index % 2 === 0 ? 'border' : 'border-none'"
          @click="feature.action"
        >
          {{ feature.buttonText }}
        </button>
      </div>
    </div>

    <div class="flex gap-4">
      <button class="border px-4 py-2">draw</button>
      <div class="flex justify-center items-center gap-4">
        <button>chat</button>
        <i-mdi-chevron-right class="w-6 h-6 text-black" />
      </div>
    </div>
  </div>

  <!-- Thank You Badge Modal -->
  <!-- <div v-if="showBadge" class="thank-you-modal">
    <div class="modal-content">
      <h2>Thank You!</h2>
      <p>You've made a difference today!</p>
      <button @click="closeBadge">Close</button>
    </div>
  </div> -->
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
