<template>

   
    <!-- Features Section -->
    <section id="features" class="features">
      <h2>Our Features</h2>
      <div class="features-grid">
        <ChildFriendlyCard v-for="(feature, index) in features" :key="index">
          <template #header>
            <h3>{{ feature.title }}</h3>
          </template>
          <template>
            <p>{{ feature.description }}</p>
          </template>
          <template #footer>
            <button class="card-button" @click="feature.action">
              {{ feature.buttonText }}
            </button>
          </template>
        </ChildFriendlyCard>
      </div>
    </section>

   
    <!-- Thank You Badge Modal -->
    <div v-if="showBadge" class="thank-you-modal">
      <div class="modal-content">
        <h2>Thank You!</h2>
        <p>You've made a difference today!</p>
        <button @click="closeBadge">Close</button>
      </div>
    </div>

</template>

<script>
  import ChildFriendlyCard from "@/components/ChildFriendlyCard.vue";

  export default {
    components: {
      ChildFriendlyCard,
    },
    data() {
      return {
        showBadge: false,
        features: [
          {
            title: "Friendly Support",
            description: "Reach out to trained professionals for guidance and help.",
            buttonText: "Learn More",
            action: this.navigateToHelp,
          },
          {
            title: "Interactive Games",
            description: "Engage with activities that teach and entertain.",
            buttonText: "Play Games",
            action: this.navigateToGames,
          },
          {
            title: "Safe Sharing",
            description: "Share your story in a secure and non-judgmental environment.",
            buttonText: "Share Now",
            action: this.navigateToSafeSharing,
          },
        ],
      };
    },
    methods: {
      navigateToStart() {
        this.$router.push("/start");
      },
      navigateToGames() {
        this.$router.push("/interactive-games");
      },
      navigateToHelp() {
        this.$router.push("/child-help");
      },
      navigateToSafeSharing() {
        this.$router.push("/safe-sharing");
      },
      closeBadge() {
        this.showBadge = false;
      },
    },
  };
</script>

<style scoped>
  
</style>
