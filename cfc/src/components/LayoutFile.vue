<template>
    <div class="landing-page">
        <!-- Header Section -->
        <header class="header">
            <NavBar />
        </header>

        <!-- Hero Section -->
        <section class="hero">
            <HeroPage />
        </section>

        <!-- Features Section -->
        <section id="features" class="features">
            < <RouterView />

        </section>

        <!-- Footer Section -->
        <footer class="footer">
            <p>&copy; 2024 SAUTI. All Rights Reserved.</p>
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
    import ChildFriendlyCard from "@/components/ChildFriendlyCard.vue";
    import NavBar from "./NavBar.vue";
import HeroPage from "./HeroPage.vue";

    export default {
        components: {
            ChildFriendlyCard,
            NavBar,
            HeroPage
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
