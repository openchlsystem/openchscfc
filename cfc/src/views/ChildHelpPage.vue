<template>
  <div class="px-4 sm:px-6 md:px-10 lg:px-20">
    <!-- Header -->
    <header class="flex flex-col gap-4 py-12">
      <h3 class="font-header font-bold">Hello</h3>
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-header">
        We're Here to Help
      </h2>
      <p class="text-base sm:text-lg max-w-2xl">
        If you have questions or need support, please don’t hesitate to reach out to us!
      </p>
      <button @click="scrollToChat" class="bg-black text-white px-6 py-3 rounded-md w-fit">Talk to us</button>
    </header>

    <!-- Contact Info and Image -->
    <div class="flex flex-col lg:flex-row gap-12 py-12">
      <!-- Contact Info -->
      <div class="flex flex-col gap-10 w-full lg:w-1/2">
        <div class="flex flex-col gap-4">
          <i-mdi-email class="w-6 h-6 text-black" />
          <h2 class="font-bold text-xl font-header">Email</h2>
          <p>support@childhelpsystem.com</p>
          <p class="underline">hello@CHSystem.io</p>
        </div>
        <div class="flex flex-col gap-4">
          <i-mdi-phone class="w-6 h-6 text-black" />
          <h2 class="font-bold text-xl font-header">Phone</h2>
          <p>Call us anytime!</p>
          <p class="underline">+1 (555) 000-0000</p>
        </div>
        <div class="flex flex-col gap-4">
          <i-mdi-map-marker class="w-6 h-6 text-black" />
          <h2 class="font-bold text-xl font-header">Office</h2>
          <p>123 Sample St, Sydney NSW 2000 AU</p>
        </div>
      </div>

      <!-- Image -->
      <div class="w-full lg:w-1/2">
        <img
          src="https://imgs.search.brave.com/a4ZTHrZwdH2-zrSmfFM1xODUI-_3QOACAWowJLbsExo/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvOTUw/NjA1MDQ2L3Bob3Rv/L211bHRpZXRobmlj/LWNoaWxkcmVuLWlu/LWEtY2lyY2xlLmpw/Zz9zPTYxMng2MTIm/dz0wJms9MjAmYz1I/YXd6V0g4ZkJ6c0pT/dXp2aXV1UzNpUmhS/UEF3RVcyUE9RVExR/M0x6VWZZPQ"
          alt="Happy children illustration"
          class="w-full max-w-md lg:max-w-xl rounded-xl object-cover"
        />
      </div>
    </div>

    <!-- Chat Section -->
    <div class="flex flex-col lg:flex-row gap-8 py-12 bg-white">
      <!-- Left Text -->
      <div class="flex flex-col gap-4 w-full lg:w-1/2">
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-header">
          Talk to us
        </h2>
        <p class="text-base sm:text-lg">We’re here to listen and help you.</p>
      </div>

      <!-- Chat Box -->
      <section class="flex flex-col w-full lg:w-1/2 bg-white rounded-lg shadow-md p-4">
        <!-- Chat Messages -->
        <div
          ref="chatContainer"
          class="flex flex-col gap-3 overflow-y-auto h-96 p-3 rounded bg-gray-200 "
        >
          <div
            v-for="(message, index) in messages"
            :key="index"
            :class="[
              'p-3 max-w-[75%] rounded-lg text-sm break-words',
              message.type === 'user'
                ? 'self-end bg-black text-white'
                : 'self-start bg-white text-black'
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
            class="px-4 py-3 bg-black text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
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
    
  scrollToBottom() {
    const container = this.$refs.chatContainer
    if (container) {
      container.scrollTo({
        top: container.scrollHeight,
        behavior: 'smooth',
      })
    }
  },
  scrollToChat() {
    const section = this.$refs.chatSection
    if (section) {
      section.scrollIntoView({ behavior: 'smooth' })
    }
  },

  },
}
</script>


