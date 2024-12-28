<template>
    <div class="landing-page">
        <!-- Header Section -->
        <header class="header">
            <nav class="nav-bar">
                <div class="logo">SAUTI</div>
                <ul class="nav-links">
                    <li><a href="#features">Features</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </header>

        <!-- Hero Section -->
        <section class="hero">
            <div class="hero-content">
                <h1>Welcome to SAUTI</h1>
                <p>A safe space for children and families. Share your voice, find help, and grow stronger together.</p>
                <button @click="navigateToStart">Get Started</button>
            </div>
            <div class="hero-animation">
                <!-- <img src="/path/to/hero-animation.svg" alt="Hero Animation" /> -->
            </div>
        </section>

        <!-- Features Section -->
        <section id="features" class="features">
            <h2>Our Features</h2>
            <div class="features-grid">
                <div class="feature" @click="navigateToHelp">
                    <!-- <img src="/path/to/icon1.svg" alt="Feature 1" /> -->
                    <h3>Friendly Support</h3>
                    <p>Reach out to trained professionals for guidance and help.</p>
                </div>
                <div class="feature" @click="navigateToGames">
                    <!-- <img src="/path/to/icon2.svg" alt="Feature 2" /> -->
                    <h3>Interactive Games</h3>
                    <p>Engage with activities that teach and entertain.</p>
                </div>
                <div class="feature" @click="navigateToSafeSharing">
                    <!-- <img src="/path/to/icon3.svg" alt="Feature 3" /> -->
                    <h3>Safe Sharing</h3>
                    <p>Share your story in a secure and non-judgmental environment.</p>
                </div>
            </div>
        </section>

        <!-- Footer Section -->
        <footer class="footer">
            <p>&copy; 2024 SAUTI. All Rights Reserved.</p>
        </footer>

        <!-- Thank You Badge Modal -->
        <div v-if="showBadge" class="thank-you-modal">
            <div class="modal-content">
                <!-- <img src="/path/to/badge.svg" alt="Thank You Badge" /> -->
                <h2>Thank You!</h2>
                <p>You've made a difference today!</p>
                <button @click="closeBadge">Close</button>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
      return {
        showBadge: false
      }
    },
    methods: {
      navigateToStart() {
        this.$router.push('/start');
        },
      navigateToGames() {
          this.$router.push('/interactive-games');
        },
      navigateToHelp() {
          this.$router.push('/child-help');
        },

        navigateToSafeSharing() {
            this.$router.push('/safe-sharing');
        },
      closeBadge() {
        this.showBadge = false;
      }
    }
}
</script>

<style scoped>

    
</style>
