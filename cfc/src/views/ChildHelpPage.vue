<template>
    <div class="child-help-page">
        <header class="header">
            <h1>We're Here to Help</h1>
            <p>Feel free to share anything. You're safe here.</p>
        </header>

        <div class="chat-container">
            <div class="chat-window">
                <div v-for="(message, index) in messages" :key="index" :class="message.type">
                    <p>{{ message.text }}</p>
                </div>
            </div>
            <form @submit.prevent="sendMessage" class="chat-input">
                <input v-model="userInput" type="text" placeholder="Type your message..."
                    aria-label="Type your message" />
                <button type="submit">Send</button>
            </form>
        </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                userInput: "",
                messages: [
                    { text: "Hello! I'm here to help. How are you feeling today?", type: "bot" },
                ],
            };
        },
        methods: {
            sendMessage() {
                if (this.userInput.trim() === "") return;

                // Add user's message to the chat
                this.messages.push({ text: this.userInput, type: "user" });

                // Clear the input field
                const input = this.userInput;
                this.userInput = "";

                // Generate automated response
                setTimeout(() => {
                    this.generateResponse(input);
                }, 1000);
            },
            generateResponse(input) {
                // Simple keyword-based response logic
                let response = "That's interesting. Can you tell me more?";
                if (input.toLowerCase().includes("sad")) {
                    response = "I'm sorry to hear you're feeling sad. Want to tell me why?";
                } else if (input.toLowerCase().includes("scared")) {
                    response = "It’s okay to feel scared sometimes. Do you want to talk about it?";
                } else if (input.toLowerCase().includes("happy")) {
                    response = "I’m glad you’re feeling happy! What’s making you feel that way?";
                }

                // Add the bot's response to the chat
                this.messages.push({ text: response, type: "bot" });
            },
        },
    };
</script>

<style scoped>
    .child-help-page {
        font-family: 'Comic Sans MS', 'Arial', sans-serif;
        padding: 20px;
        max-width: 600px;
        margin: 0 auto;
        background-color: #fdf1ff;
        /* Light lavender for a soft and welcoming feel */

        /* Bright pink border for a friendly look */
        border-radius: 20px;
        box-shadow: 0 6px 14px rgba(255, 128, 171, 0.3);
    }

  

    
    .chat-container {
        display: flex;
        flex-direction: column;
        background-color: #ffffff;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(255, 128, 171, 0.15);
    }

    .chat-window {
        overflow-y: auto;
        margin-bottom: 15px;
        padding: 15px;
        background: #fff8e1;
        /* Light pastel yellow for warmth */
        border-radius: 20px;
        scrollbar-width: thin;
        scrollbar-color: #ff80ab transparent;
        min-height: 300px;
    }

    .chat-window .bot {
        background-color: #b2fab4;
        /* Soft green for calmness */
        color: #2e7d32;
        padding: 12px;
        border-radius: 15px 15px 15px 5px;
        margin-bottom: 12px;
        align-self: flex-start;
        max-width: 75%;
        word-wrap: break-word;
        box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.05);
        font-style: italic;
    }

    .chat-window .user {
        background-color: #ffccbc;
        /* Warm orange for energy */
        color: #bf360c;
        padding: 12px;
        border-radius: 15px 15px 5px 15px;
        margin-bottom: 12px;
        align-self: flex-end;
        max-width: 75%;
        word-wrap: break-word;
        box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.05);
    }

    

   

    @media (max-width: 600px) {
        .child-help-page {
            padding: 12px;
        }

        .header h1 {
            font-size: 2rem;
        }

        .header p {
            font-size: 1rem;
        }

        .chat-window {
            min-height: 250px;
        }

        .chat-input input {
            font-size: 0.9rem;
        }

        .chat-input button {
            font-size: 0.9rem;
            padding: 10px 18px;
        }
    }
</style>


