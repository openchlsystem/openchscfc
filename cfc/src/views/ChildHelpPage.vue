<template>
  <div class="bg-background pb-20 px-4 pt-24 sm:px-6 md:px-10 lg:px-20 flex flex-col gap-20">
    <!-- Header -->
    <header class="flex flex-col gap-4 py-12 text-center lg:text-left">
      <h3 class="font-header font-bold">Hello</h3>
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-header">
        We're Here to Help
      </h2>
      <p class="text-base sm:text-lg max-w-2xl font-text mx-auto lg:mx-0">
        If you have questions or need support, please don’t hesitate to reach out to us!
      </p>
    </header>

    <!-- Contact Info and Image -->
    <div class="flex flex-col lg:flex-row gap-12 py-12 px-6 sm:px-8 bg-component1 rounded-2xl shadow-lg">
      <!-- Contact Info -->
      <div class="flex flex-col gap-10 w-full lg:w-1/2">
        <div class="flex flex-col gap-4">
          <i-mdi-email class="w-6 h-6 text-black" />
          <h2 class="font-bold text-xl font-header">Email</h2>
          <p class="font-text break-words">support@childhelpsystem.com</p>
          <p class="underline font-text break-words">hello@CHSystem.io</p>
        </div>

        <div class="flex flex-col gap-4">
          <i-mdi-phone class="w-6 h-6 text-black" />
          <h2 class="font-bold text-xl font-header">Phone</h2>
          <p class="font-text">Call us anytime!</p>
          <p class="underline font-text">+1 (555) 000-0000</p>
        </div>

        <div class="flex flex-col gap-4">
          <i-mdi-map-marker class="w-6 h-6 text-black" />
          <h2 class="font-bold text-xl font-header">Office</h2>
          <p class="font-text">123 Sample St, Sydney NSW 2000 AU</p>
        </div>
      </div>

      <!-- Image -->
      <div class="w-full lg:w-1/2 flex justify-center">
        <img
          src="../assets/images/kids.jpeg"
          alt="Happy children illustration"
          class="w-full max-w-md sm:max-w-lg lg:max-w-xl rounded-xl object-cover"
        />
      </div>
    </div>

    <!-- Chat Section -->
    <div class="flex flex-col lg:flex-row gap-8 py-12 px-6 sm:px-8 bg-component2 rounded-2xl shadow-lg">
      <!-- Left Text -->
      <div class="flex flex-col gap-4 w-full lg:w-1/2 text-center lg:text-left">
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-header">Talk to us</h2>
        <p class="text-base sm:text-lg font-text">We’re here to listen and help you.</p>
      </div>

      <!-- Chat Box -->
      <section class="flex flex-col w-full lg:w-1/2 bg-white shadow-xl rounded-lg p-4">
        <!-- Chat Messages -->
        <div
          ref="chatContainer"
          id="chat-section"
          class="flex flex-col gap-3 overflow-y-auto h-96 p-3 rounded bg-blue-50"
        >
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="[ 
              'p-3 max-w-[85%] rounded-lg text-sm break-words',
              message.type === 'user'
                ? 'self-end font-header bg-button text-black'
                : 'self-start font-header bg-component1 text-black'
            ]"
          >
            <p>{{ message.text }}</p>
          </div>
        </div>

        <!-- Input -->
        <form @submit.prevent="sendMessage" class="mt-4 flex flex-col sm:flex-row gap-2">
          <input
            v-model="userInput"
            type="text"
            :placeholder="currentPrompt.placeholder"
            :disabled="isSubmitting"
            class="flex-1 p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
          />
          <button
            type="submit"
            :disabled="isSubmitting"
            class="px-4 py-3 bg-button text-white rounded-xl hover:bg-component1 disabled:bg-gray-400 disabled:text-red-500"
          >
            Send
          </button>
        </form>
      </section>
    </div>
  </div>
</template>


<script>
export default {
  data() {
    return {
      userInput: '',
      messages: [
        {
          text: "Hello! I'm here to help you sign up. What's your name? 😊",
          type: 'bot',
        },
      ],
      form: {
        name: '',
        age: null,
        gender: '',
        parentEmail: '',
        interests: '',
        consent: false,
      },
      currentStep: 'name',
      isSubmitting: false,
      prompts: {
        name: { text: "What's your name? 😊", placeholder: 'Enter your first name' },
        age: { text: 'How old are you? 🎂', placeholder: 'Enter your age (1-18)' },
        gender: {
          text: "What's your gender? 🧒",
          placeholder: 'Enter: boy, girl, other, or prefer not to say',
        },
        parentEmail: {
          text: 'Parent/Guardian Email 📧',
          placeholder: "Enter your parent's email",
        },
        interests: {
          text: 'What do you like? 🌈',
          placeholder: 'E.g., games, books, sports',
        },
        consent: {
          text: "Do you have your parent's/guardian's permission to sign up? Type 'yes' to confirm. ✅",
          placeholder: "Type 'yes' or 'no'",
        },
        finished: {
          text: "Thank you for signing up! 🎉 You're all set to begin.",
          placeholder: '',
        },
      },
    }
  },
  computed: {
    currentPrompt() {
      return this.prompts[this.currentStep]
    },
  },
  methods: {
    sendMessage() {
      if (this.userInput.trim() === '') return

      this.messages.push({ text: this.userInput, type: 'user' })
      const input = this.userInput.trim()
      this.userInput = ''

      this.$nextTick(() => {
        this.scrollToBottom()
      })

      setTimeout(() => {
        this.handleResponse(input)
      }, 500)
    },
    handleResponse(input) {
      if (this.currentStep === 'name') {
        this.form.name = input
        this.advanceStep('age')
      } else if (this.currentStep === 'age') {
        const age = parseInt(input, 10)
        if (age >= 1 && age <= 18) {
          this.form.age = age
          this.advanceStep('gender')
        } else {
          this.addBotMessage('Please enter a valid age between 1 and 18.')
        }
      } else if (this.currentStep === 'gender') {
        const validGenders = ['boy', 'girl', 'other', 'prefer not to say']
        if (validGenders.includes(input.toLowerCase())) {
          this.form.gender = input
          this.advanceStep('parentEmail')
        } else {
          this.addBotMessage('Please enter a valid gender option.')
        }
      } else if (this.currentStep === 'parentEmail') {
        if (this.validateEmail(input)) {
          this.form.parentEmail = input
          this.advanceStep('interests')
        } else {
          this.addBotMessage('Please enter a valid email address.')
        }
      } else if (this.currentStep === 'interests') {
        this.form.interests = input
        this.advanceStep('consent')
      } else if (this.currentStep === 'consent') {
        if (input.toLowerCase() === 'yes') {
          this.form.consent = true
          this.advanceStep('finished')
        } else {
          this.addBotMessage("You need your parent's/guardian's permission to sign up.")
        }
      }
    },
    advanceStep(nextStep) {
      this.currentStep = nextStep
      const prompt = this.prompts[nextStep]
      if (prompt) {
        this.addBotMessage(prompt.text)
      }

      if (nextStep === 'finished') {
        console.log('Collected Form Data:', this.form)
      }
    },
    addBotMessage(text) {
      this.messages.push({ text, type: 'bot' })
      this.$nextTick(() => {
        this.scrollToBottom()
      })
    },
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
    scrollToBottom() {
      const container = this.$refs.chatContainer
      if (container) {
        container.scrollTo({
          top: container.scrollHeight,
          behavior: 'smooth',
        })
      }
    },

  },
}
</script>
