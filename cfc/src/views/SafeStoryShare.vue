<template>
    <div class="safe-sharing-container">
        <!-- Header Section -->
        <header class="safe-sharing-header">
            <h1>Welcome to Safe Sharing!</h1>
            <p>Express yourself in a secure and non-judgmental environment.</p>
        </header>

        <!-- Features Section -->
        <section class="features">
            <div class="feature-card" v-for="feature in features" :key="feature.title">
                <img :src="feature.icon" :alt="feature.title" class="feature-icon" />
                <h3>{{ feature.title }}</h3>
                <p>{{ feature.description }}</p>
            </div>
        </section>

        <!-- Mood Selector -->
        <section class="mood-selector">
            <h2>How are you feeling today?</h2>
            <div class="mood-options">
                <button v-for="mood in moods" :key="mood.name"
                    :class="['mood-button', { selected: mood.name === selectedMood }]" @click="selectMood(mood.name)">
                    <img :src="mood.icon" :alt="mood.name" />
                    <span>{{ mood.name }}</span>
                </button>
            </div>
        </section>

        <!-- Story Prompt Section -->
        <section class="story-prompt">
            <h2>Share Your Story</h2>
            <p class="prompt">{{ prompt }}</p>
            <textarea v-model="story" placeholder="Type your story here..." class="story-input"></textarea>
            <button class="share-button" @click="shareStory">Share Now</button>
        </section>

        <!-- Drawing Board -->
        <section class="drawing-board">
            <h2>Draw Your Feelings</h2>
            <canvas ref="drawingCanvas" class="canvas"></canvas>
            <button class="clear-drawing" @click="clearCanvas">Clear Drawing</button>
        </section>

        <!-- Support Section -->
        <section class="support">
            <h2>Need Help?</h2>
            <p>We’re here for you anytime. Reach out to us below:</p>
            <button class="contact-button">Chat with Us</button>
        </section>
    </div>
</template>

<script>
    import angryIcon from "@/assets/Icons/angry_11732053.png";
    import sadIcon from "@/assets/Icons/sad-face_11068997.png";
    import confuseIcon from "@/assets/Icons/confused_4818761.png";
    import happyIcon from "@/assets/Icons/winking-face_10963369.png";
    import confidential from "@/assets/Icons/confidential_16659660.png";
    import interactive from "@/assets/Icons/interaction_11296524.png";
    import supportive from "@/assets/Icons/supportive_16137493.png";
    export default {
        data() {
            return {
                features: [
                    {
                        icon: confidential,
                        title: "Confidentiality Guarantee",
                        description: "Your stories are private and protected.",
                    },
                    {
                        icon:interactive,
                        title: "Interactive Sharing",
                        description: "Express yourself with text, voice, or emojis.",
                    },
                    {
                        icon: supportive,
                        title: "Supportive Responses",
                        description: "Receive kind replies from our trained helpers.",
                    },
                ],
                moods: [
                    { name: "Happy", icon: happyIcon },
                    { name: "Sad", icon: sadIcon },
                    { name: "Angry", icon: angryIcon },
                    { name: "Confused", icon: confuseIcon },
                ],
                selectedMood: null,
                story: "",
                prompt: "What made you smile today?",
            };
        },
        methods: {
            selectMood(mood) {
                this.selectedMood = mood;
            },
            shareStory() {
                if (this.story.trim()) {
                    alert("Thank you for sharing your story!");
                    this.story = "";
                } else {
                    alert("Please write something before sharing.");
                }
            },
            clearCanvas() {
                const canvas = this.$refs.drawingCanvas;
                const context = canvas.getContext("2d");
                context.clearRect(0, 0, canvas.width, canvas.height);
            },
        },
        mounted() {
            const canvas = this.$refs.drawingCanvas;
            const context = canvas.getContext("2d");

            canvas.width = 300;
            canvas.height = 300;

            canvas.addEventListener("mousedown", (e) => {
                context.beginPath();
                context.moveTo(e.offsetX, e.offsetY);
                canvas.addEventListener("mousemove", draw);
            });

            canvas.addEventListener("mouseup", () => {
                canvas.removeEventListener("mousemove", draw);
            });

            const draw = (e) => {
                context.lineTo(e.offsetX, e.offsetY);
                context.strokeStyle = "black";
                context.lineWidth = 2;
                context.stroke();
            };
        },
    };
</script>

<style scoped>
    .safe-sharing-container {
        font-family: 'Poppins', sans-serif;
        padding: 20px;
        color: #333;
    }

    .safe-sharing-header {
        text-align: center;
    }

    .features {
        display: flex;
        justify-content: space-around;
        margin: 20px 0;
    }

    .feature-card {
        text-align: center;
    }

    .feature-icon {
        width: 50px;
        height: 50px;
    }

    .mood-selector {
        text-align: center;
        margin: 20px 0;
    }

    .mood-options {
        display: flex;
        justify-content: center;
        gap: 10px;
    }

    .mood-button {
        display: flex;
        flex-direction: column;
        align-items: center;
        border: none;
        background: none;
        cursor: pointer;
    }

    .mood-button.selected {
        border: 2px solid #4CAF50;
    }

    .story-prompt {
        margin: 20px 0;
        text-align: center;
    }

    .story-input {
        width: 100%;
        height: 100px;
        padding: 10px;
        margin: 10px 0;
    }

    .share-button {
        padding: 10px 20px;
        background-color: #4CAF50;
        color: #fff;
        border: none;
        cursor: pointer;
    }

    .drawing-board {
        text-align: center;
    }

    .canvas {
        border: 1px solid #ccc;
        display: block;
        margin: 10px auto;
    }

    .clear-drawing {
        margin: 10px 0;
        padding: 10px;
        background-color: #f44336;
        color: white;
        border: none;
        cursor: pointer;
    }

    .support {
        text-align: center;
    }

    .contact-button {
        padding: 10px 20px;
        background-color: #2196F3;
        color: white;
        border: none;
        cursor: pointer;
    }
</style>
