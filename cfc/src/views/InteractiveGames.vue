<template>
  <div class="bg-background min-h-screen pt-32">
    <h1 class="text-3xl font-header sm:text-4xl lg:text-5xl font-bold  mb-10 text-center">
      Interactive Games
    </h1>

    <div class="flex flex-wrap justify-center items-start gap-4 md:gap-8 p-4">
  <ChildFriendlyCard v-for="game in games" :key="game.title">
    <template #header>
      <h2 class="text-xl font-semibold font-header text-purple-900">{{ game.title }}</h2>
    </template>
    <p class="font-text">{{ game.description }}</p>
    <template #footer>
      <button
        @click="goToGame(game.link)"
        class="bg-button hover:text-purple-900 text-white font-header px-4 py-2 rounded-md hover:bg-purple-100 transition"
      >
        Play Now
      </button>
    </template>
  </ChildFriendlyCard>
</div>

  </div>
</template>
 
<script>
export default {
  methods: {
    goToGame(link) {
      this.$router.push(link)
    },
  },
  data() {
    return {
      games: [
        { title: 'Memory Match', description: 'Test your memory with this fun matching game!', link: '/games/memory-match' },
        { title: 'Math Puzzle', description: 'Sharpen your math skills with exciting puzzles!', link: '/games/math-puzzle' },
        { title: 'Word Scramble', description: 'Unscramble the letters to form meaningful words.', link: '/games/word-scramble' },
        { title: 'Coloring Fun', description: 'Unleash your creativity with virtual coloring!', link: '/games/coloring-fun' },
      ],
    }
  },
}
</script>


