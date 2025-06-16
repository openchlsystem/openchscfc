<template>
  <div class="px-20">
    <!-- Header Section -->
    <header class="flex gap-20 items-start py-16">
      <h1 class="text-5xl font-extrabold font-header w-1/2">Welcome to Feelings Hub</h1>
      <p class="w-1/2 text-lg">
        Here in the Feelings Hub, we understand that it's okay to have different emotions. Let's
        explore how you're feeling together in a safe and friendly space!.
      </p>
    </header>

    <!-- Features Section -->
    <!-- <section class="features">
      <div class="feature-card" v-for="feature in features" :key="feature.title">
        <img :src="feature.icon" :alt="feature.title" class="feature-icon" />
        <h3>{{ feature.title }}</h3>
        <p>{{ feature.description }}</p>
      </div>
    </section> -->

    <div class="flex gap-20 py-24">
      <!-- Mood Selector -->
      <section class="w-1/2 flex flex-col gap-4">
        <h3 class="font-header font-bold">Feelings</h3>

        <h2 class="font-header font-bold text-5xl">Express Your Emotions with Fun Emojis</h2>

        <p class="text-lg max-w-xl">
          Discover a world of feelings through our interactive emoji selection. Choose the emoji
          that best represents your emotions and share your thoughts.
        </p>

        <div class="flex flex-col gap-2">
          <h3 class="font-header font-bold text-xl">Choose Emotion</h3>
          <p>Select an emoji to express how you feel today!</p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
          <button
            v-for="mood in moods"
            :key="mood.name"
            :class="[
              'flex flex-col items-center justify-center p-4 rounded-xl transition-all duration-200 shadow hover:shadow-lg hover:bg-slate-100',
              mood.name === selectedMood ? 'bg-slate-200 font-semibold' : 'bg-white',
            ]"
            @click="selectMood(mood.name)"
          >
            <img :src="mood.icon" :alt="mood.name" class="w-12 h-12 mb-2" />
            <span class="text-base">{{ mood.name }}</span>
          </button>
        </div>
      </section>

      <!-- Story Prompt Section -->
      <section class="flex flex-col gap-2 justify-center w-1/2">
        <h2 class="font-header font-bold text-xl">{{ moodBasedTitle }}</h2>
        <p class="text-gray-600">{{ moodBasedPrompt }}</p>
        <textarea
          v-model="story"
          placeholder="Type your story here..."
          class="border p-4 rounded-lg"
        ></textarea>
        <button
          class="bg-black text-white rounded-lg p-4"
          @click="shareStory"
          v-if="story.trim() !== ''"
        >
          Share Now
        </button>
      </section>
    </div>

    <!-- Drawing Board -->
    <div class="flex gap-20 py-24">
      <section class="w-1/2 flex flex-col gap-4">
       
          <DrawingBoard />
      
      </section>

      <section class="w-1/2 flex flex-col gap-4">
        <h3 class="font-header font-bold">Draw Hub</h3>

        <h2 class="font-header font-bold text-5xl">
          Express your feedback differently ,draw your feelings.
        </h2>

        <p class="text-lg max-w-xl">
          Discover a world of feelings through our interactive section.Draw oout the best drawing
          that describes your feeling :)
        </p>

        <div class="flex flex-col gap-2">
          <h3 class="font-header font-bold text-xl">Draw your Emotion</h3>
          <p>Draw how you feel today!</p>
        </div>
      </section>
    </div>

    <!-- Play Games Section -->
    <!-- <section class="play-games" v-if="activateGames">
      <h2>Play Games</h2>
      <div class="games-container">
        <InteractiveGames />
      </div>
    </section> -->

    <!-- Support Section -->
    <!-- <section class="support">
      <h2>Need Help?</h2>
      <p>We’re here for you anytime. Reach out to us below:</p>
      <button class="contact-button" @click="navigateToChildHelp">Chat with Us</button>
    </section> -->
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import angryIcon from '@/assets/Icons/angry_11732053.png'
import sadIcon from '@/assets/Icons/sad-face_11068997.png'
import confuseIcon from '@/assets/Icons/confused_4818761.png'
import happyIcon from '@/assets/Icons/winking-face_10963369.png'
import confidential from '@/assets/Icons/confidential_16659660.png'
import interactive from '@/assets/Icons/interaction_11296524.png'
import supportive from '@/assets/Icons/supportive_16137493.png'
import DrawingBoard from '@/components/DrawingBoard.vue'
import InteractiveGames from './InteractiveGames.vue'

export default {
  components: {
    DrawingBoard,
    InteractiveGames,
  },
  setup() {
    const features = ref([
      {
        icon: confidential,
        title: 'Confidentiality Guarantee',
        description: 'Your stories are private and protected.',
      },
      {
        icon: interactive,
        title: 'Interactive Sharing',
        description: 'Express yourself with text, voice, or emojis.',
      },
      {
        icon: supportive,
        title: 'Supportive Responses',
        description: 'Receive kind replies from our trained helpers.',
      },
    ])

    const moods = ref([
      { name: 'Happy', icon: happyIcon },
      { name: 'Sad', icon: sadIcon },
      { name: 'Angry', icon: angryIcon },
      { name: 'Confused', icon: confuseIcon },
    ])

    const moodPrompts = {
      Happy: {
        title: 'Share Your Joyful Moments',
        prompt: 'What made you smile or feel happy today?',
      },
      Sad: {
        title: 'Share Your Sorrows',
        prompt: "What's been troubling you? We're here to listen.",
      },
      Angry: {
        title: 'Share Your Frustrations',
        prompt: 'What made you angry? Let it out and express yourself.',
      },
      Confused: {
        title: 'Share Your Thoughts',
        prompt: "What's puzzling or confusing you? Feel free to share.",
      },
    }

    const router = useRouter()

    const selectedMood = ref(null)
    const story = ref('')

    const moodBasedTitle = computed(() =>
      selectedMood.value ? moodPrompts[selectedMood.value].title : 'Share Your Story',
    )

    const moodBasedPrompt = computed(() =>
      selectedMood.value
        ? moodPrompts[selectedMood.value].prompt
        : 'How are you feeling today? Let us know.',
    )

    const feedback = ref([])

    const selectMood = (moodName) => {
      selectedMood.value = moodName
      story.value = '' // Clear the story when changing moods
      feedback.value = '' // Clear the feedback when changing moods
    }

    const shareStory = () => {
      const trimmedStory = story.value.trim()
      if (trimmedStory) {
        console.log('Mood:', selectedMood.value)
        console.log('Story:', trimmedStory)
        activateGames.value = true
        alert('Your story has been shared!')
        story.value = ''
        feedback.value.push({
          mood: selectedMood.value,
          story: trimmedStory,
        })
      } else {
        alert('Please write something before sharing.')
      }
    }

    const drawingCanvas = ref(null)
    const activateGames = ref(false)

    const clearCanvas = () => {
      const canvas = drawingCanvas.value
      const context = canvas.getContext('2d')
      context.clearRect(0, 0, canvas.width, canvas.height)
    }

    const navigateToChildHelp = () => {
      // Implement navigation logic here
      router.push('/child-help')
    }

    onMounted(() => {
      const canvas = drawingCanvas.value
      const context = canvas.getContext('2d')

      canvas.width = 300
      canvas.height = 300

      canvas.addEventListener('mousedown', (e) => {
        context.beginPath()
        context.moveTo(e.offsetX, e.offsetY)
        canvas.addEventListener('mousemove', draw)
      })

      canvas.addEventListener('mouseup', () => {
        canvas.removeEventListener('mousemove', draw)
      })

      const draw = (e) => {
        context.lineTo(e.offsetX, e.offsetY)
        context.strokeStyle = 'black'
        context.lineWidth = 2
        context.stroke()
      }
    })

    return {
      features,
      moods,
      selectedMood,
      moodBasedTitle,
      moodBasedPrompt,
      story,
      selectMood,
      shareStory,
      clearCanvas,
      drawingCanvas,
      activateGames,
      feedback,
      navigateToChildHelp,
    }
  },
}
</script>

<style scoped>
/* Add your styles here */
</style>
