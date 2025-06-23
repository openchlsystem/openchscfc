<template>
  <div class="px-20">
    <header class="flex gap-20 items-start py-16">
      <h2 class="text-5xl font-extrabold font-header w-1/2">We're Here to Help</h2>
      <p class="w-1/2 text-lg">
        If you have questions or need support, please don’t hesitate to reach out to us!
      </p>
    </header>

    <div class="flex flex-col gap-20 py-24">

      <div class="flex flex-col gap-4">
        <h3 class="font-header font-bold">Reach</h3>

        <h2 class="font-header font-bold text-5xl">Contact Us</h2>

        <p class="text-lg max-w-xl">We’re here to help you with any questions!</p>
      </div>

      <section class=" flex  gap-20">
        <div>
          <div class="flex flex-col gap-10">
            <div class="flex flex-col gap-4">
              <i-mdi-email class="w-8 h-8 text-black" />
              <h2 class="font-bold text-xl font-header">Email</h2>
              <p>support@childhelpsystem.com</p>
              <p class="underline">hello@CHSystem.io</p>
            </div>
            <div class="flex flex-col gap-4">
              <i-mdi-phone class="w-8 h-8 text-black" />
              <h2 class="font-bold text-xl font-header">Phone</h2>
              <p>Call us anytime!</p>
              <p class="underline">+1 (555) 000-0000</p>
            </div>
            <div class="flex flex-col gap-4">
              <i-mdi-map-marker class="w-8 h-8 text-black" />
              <h2 class="font-bold text-xl font-header">Office</h2>
              <p>123 Sample St, Sydney NSW 2000 AU</p>
             
            </div>
          </div>
        </div>

         <section class=" flex flex-col gap-4">
       
      <img
        src="https://imgs.search.brave.com/a4ZTHrZwdH2-zrSmfFM1xODUI-_3QOACAWowJLbsExo/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvOTUw/NjA1MDQ2L3Bob3Rv/L211bHRpZXRobmlj/LWNoaWxkcmVuLWlu/LWEtY2lyY2xlLmpw/Zz9zPTYxMng2MTIm/dz0wJms9MjAmYz1I/YXd6V0g4ZkJ6c0pT/dXp2aXV1UzNpUmhS/UEF3RVcyUE9RVExR/M0x6VWZZPQ"
        alt="Happy children illustration"
        class="w-[838px] h-[516px] rounded-4xl object-cover"
      />
      </section>
      </section>

     
    </div>

    <div class="chat-container flex flex-col max-w-xl w-full mx-auto bg-white rounded-lg shadow-md border p-4">
  <!-- Chat Messages Window -->
  <div class="chat-window flex flex-col gap-3 overflow-y-auto h-96 p-2 border rounded bg-gray-50">
    <div
      v-for="(message, index) in messages"
      :key="index"
      :class="[
        'p-3 max-w-xs rounded-lg text-sm break-words',
        message.type === 'user'
          ? 'self-end bg-blue-500 text-white'
          : 'self-start bg-gray-200 text-gray-800'
      ]"
    >
      <p>{{ message.text }}</p>
    </div>
  </div>

  <!-- Chat Input -->
  <form @submit.prevent="sendMessage" id="chat-section" class="chat-input mt-4 flex gap-2">
    <input
      v-model="userInput"
      type="text"
      :placeholder="currentPrompt.placeholder"
      aria-label="Type your message"
      :disabled="isSubmitting"
      class="flex-1 p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400 disabled:opacity-50"
    />
    <button
      type="submit"
      :disabled="isSubmitting"
      class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed"
    >
      Send
    </button>
  </form>
</div>
<!-- <div class="chat-container">
            <div class="chat-window">
                <div v-for="(message, index) in messages" :key="index" :class="message.type">
                    <p>{{ message.text }}</p>
                </div>
            </div>
            <form @submit.prevent="sendMessage" class="chat-input">
                <input v-model="userInput" type="text" :placeholder="currentPrompt.placeholder"
                    aria-label="Type your message" :disabled="isSubmitting" />
                <button type="submit" :disabled="isSubmitting">Send</button>
            </form>
        </div> style this  -->

  </div>
</template>

<script>
export default {
  data() {
    return {
      userInput: '',
      messages: [
        { text: "Hello! I'm here to help you sign up. What's your name? 😊", type: 'bot' },
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

      // Add user's message to the chat
      this.messages.push({ text: this.userInput, type: 'user' })

      const input = this.userInput.trim()
      this.userInput = ''

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
      if (nextStep === 'finished') {
        this.addBotMessage(this.prompts[nextStep].text)
        console.log('Collected Form Data:', this.form) // Here you can handle the form submission logic.
      } else {
        this.addBotMessage(this.prompts[nextStep].text)
      }
    },
    addBotMessage(text) {
      this.messages.push({ text, type: 'bot' })
    },
    validateEmail(email) {
      const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return re.test(email)
    },
  },
}
</script>

<style scoped>
/* Retain your existing styles */
</style>
