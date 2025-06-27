<template>
  <div class="pb-16 pt-44 bg-background px-4 sm:px-6 md:px-10 lg:px-20 flex flex-col gap-20">
    <!-- Header Section -->
    <header class="flex flex-col lg:flex-row gap-8 lg:gap-20 items-start">
      <h1 class="text-3xl sm:text-4xl lg:text-5xl font-extrabold font-header w-full lg:w-1/2">
        Welcome to Feelings Hub
      </h1>
      <p class="text-base font-text sm:text-lg w-full lg:w-1/2">
        Here in the Feelings Hub, we understand that it's okay to have different emotions. Let's
        explore how you're feeling together in a safe and friendly space!
      </p>
    </header>

    <!-- Mood Selector and Story Prompt Section -->
    <div class="flex flex-col lg:flex-row gap-12 lg:gap-20 py-10 px-8 rounded-3xl shadow-lg bg-component2">
      <!-- Mood Selector -->
      <section class="flex flex-col gap-4 w-full lg:w-1/2">
        <h3 class="font-header font-bold ">Feelings</h3>
        <h2 class="font-header font-bold text-3xl sm:text-4xl lg:text-5xl ">
          Express Your Emotions with Fun Emojis
        </h2>
        <p class="text-base sm:text-lg max-w-xl font-text">
          Discover a world of feelings through our interactive emoji selection. Choose the emoji
          that best represents your emotions and share your thoughts.
        </p>

        <div class="flex flex-col gap-2">
          <h3 class="font-header font-bold text-xl ">Choose Emotion</h3>
          <p class="font-text">Select an emoji to express how you feel today!</p>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
          <button
            v-for="mood in moods"
            :key="mood.name"
            :class="[
              'flex flex-col items-center justify-center p-4 rounded-xl transition-all duration-200 shadow hover:shadow-lg hover:bg-orange-200',
              mood.name === selectedMood ? 'bg-button font-semibold' : 'bg-white',
            ]"
            @click="selectMood(mood.name)"
          >
            <img :src="mood.icon" :alt="mood.name" class="w-10 h-10 mb-2" />
            <span class="text-sm text-black  font-header">{{ mood.name }}</span>
          </button>
        </div>
      </section>

      <!-- Story Prompt -->
      <section class="flex flex-col gap-4 w-full md:justify-center lg:w-1/2">
        <h2 class="font-header font-bold text-xl font text-subtitle">{{ moodBasedTitle }}</h2>
        <p class="text-gray-600">{{ moodBasedPrompt }}</p>
        <textarea
          v-model="story"
          placeholder="Type your story here..."
          class="p-4 bg-white rounded-lg min-h-[150px]"
        ></textarea>
        <button
          class="bg-button text-white rounded-2xl font-header p-4 w-full sm:w-fit"
          @click="shareStory"
          v-if="story.trim() !== ''"
        >
          Share Now
        </button>
      </section>
    </div>

    <!-- Drawing Board Section -->
    <div id="draw-section" class="flex flex-col lg:flex-row gap-12 lg:gap-20 py-10 px-8 rounded-3xl shadow-lg bg-component1">
      <!-- Drawing Board -->
      <section class=" lg:w-1/2 flex flex-col gap-4">
        <DrawingBoard />
      </section>

      <!-- Drawing Info -->
      <section class="w-full lg:w-1/2 flex flex-col gap-4">
        <h3 class="font-header font-bold ">Draw Hub</h3>
        <h2 class="font-header font-bold text-3xl sm:text-4xl lg:text-5xl">
          Express your feedback differently, draw your feelings.
        </h2>
        <p class="text-base sm:text-lg max-w-xl font-text">
          Discover a world of feelings through our interactive section. Draw out the best drawing
          that describes your feeling :)
        </p>
        <div class="flex flex-col gap-2">
          <h3 class="font-header font-bold text-xl ">Draw your Emotion</h3>
          <p class="font-text">Draw how you feel today!</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import angryIcon from '@/assets/Icons/angry_11732053.png'
import sadIcon from '@/assets/Icons/sad-face_11068997.png'
import confuseIcon from '@/assets/Icons/confused_4818761.png'
import happyIcon from '@/assets/Icons/winking-face_10963369.png'
import DrawingBoard from '@/components/DrawingBoard.vue'

export default {
  components: {
    DrawingBoard,
  },
  setup() {
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

    const selectedMood = ref(null)
    const story = ref('')
    const activateGames = ref(false)
    const feedback = ref([])

    const moodBasedTitle = computed(() =>
      selectedMood.value ? moodPrompts[selectedMood.value].title : 'Share Your Story',
    )

    const moodBasedPrompt = computed(() =>
      selectedMood.value
        ? moodPrompts[selectedMood.value].prompt
        : 'How are you feeling today? Let us know.',
    )

    const selectMood = (moodName) => {
      selectedMood.value = moodName
      story.value = ''
      feedback.value = []
    }

    const shareStory = () => {
      const trimmedStory = story.value.trim()
      if (trimmedStory) {
        console.log('Mood:', selectedMood.value)
        console.log('Story:', trimmedStory)
        activateGames.value = true
        alert('Your story has been shared!')
        feedback.value.push({
          mood: selectedMood.value,
          story: trimmedStory,
        })
        story.value = ''
      } else {
        alert('Please write something before sharing.')
      }
    }

    return {
      moods,
      selectedMood,
      story,
      moodBasedTitle,
      moodBasedPrompt,
      selectMood,
      shareStory,
      activateGames,
      feedback,
    }
  },
}
</script>

<style scoped>
/* Add custom styles if needed */
</style>
