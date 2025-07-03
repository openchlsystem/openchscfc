<template>
  <div class="min-h-screen flex flex-col justify-center items-center bg-[#fff59d] p-6 pt-40">
    <h1 class="text-4xl font-header font-bold text-darktext mb-2">Memory Match Game</h1>
    <p v-if="!gameStarted" class="text-md text-darktext mb-4 font-text text-center">
      Tap a card to start the game!
    </p>

    <!-- Grid Layout for Cards -->
    <div class="grid grid-cols-3 sm:grid-cols-4 gap-4 w-full max-w-lg bg-white p-6 rounded-xl shadow-md">
      <div
        v-for="(card, index) in shuffledCards"
        :key="index"
        class="relative w-full aspect-square cursor-pointer bg-button rounded-lg shadow-md"
        @click="flipCard(card, index)"
      >
        <div class="absolute inset-0 flex items-center justify-center">
          <!-- Show Front if Flipped or Matched -->
          <img
            v-if="card.flipped || card.matched"
            :src="card.image"
            alt="Card front"
            class="w-full h-full object-contain rounded-lg"
          />
          <!-- Show Back if Not Flipped -->
          <div
            v-else
            class="w-full h-full bg-button rounded-lg flex items-center justify-center text-white text-4xl font-header"
          >
            ?
          </div>
        </div>
      </div>
    </div>

    <!-- Win Message -->
    <div
      v-if="gameWon"
      class="mt-6 bg-white p-4 rounded-xl shadow-md flex flex-col items-center gap-4 w-full max-w-lg"
    >
      <h2 class="text-2xl font-header font-bold text-green-700">Yay! You Won!</h2>
      <button
        @click="resetGame"
        class="bg-button text-white font-header px-4 py-2 rounded-md hover:text-purple-900 hover:bg-purple-100 transition w-full"
      >
        Play Again
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// ✅ Import local fruit images
import apple from '../assets/images/apple.jpeg'
import banana from '../assets/images/banana.jpeg'
import grapes from '../assets/images/grapes.jpeg'
import orange from '../assets/images/orange.jpeg'
import pineapple from '../assets/images/pineapple.jpeg'
import strawberry from '../assets/images/strawberry.jpeg'

// 🃏 Original card deck (2 of each)
const originalCards = [
  { image: apple, flipped: false, matched: false },
  { image: apple, flipped: false, matched: false },
  { image: banana, flipped: false, matched: false },
  { image: banana, flipped: false, matched: false },
  { image: grapes, flipped: false, matched: false },
  { image: grapes, flipped: false, matched: false },
  { image: orange, flipped: false, matched: false },
  { image: orange, flipped: false, matched: false },
  { image: pineapple, flipped: false, matched: false },
  { image: pineapple, flipped: false, matched: false },
  { image: strawberry, flipped: false, matched: false },
  { image: strawberry, flipped: false, matched: false },
]

const cards = ref([])
const flippedCards = ref([])
const gameWon = ref(false)
const gameStarted = ref(false)

// 🃏 Shuffle the cards each game
const shuffledCards = computed(() => {
  return [...cards.value].sort(() => Math.random() - 0.5)
})

const startGame = () => {
  cards.value = originalCards.map(card => ({ ...card }))
  gameStarted.value = true
}

const resetGame = () => {
  cards.value = originalCards.map(card => ({
    ...card,
    flipped: false,
    matched: false
  }))
  flippedCards.value = []
  gameWon.value = false
  gameStarted.value = false
}

const checkGameWon = () => {
  gameWon.value = cards.value.every(card => card.matched)
}

const flipCard = (card, index) => {
  if (!gameStarted.value) startGame()

  if (flippedCards.value.length < 2 && !card.flipped && !card.matched) {
    card.flipped = true
    flippedCards.value.push({ card, index })

    if (flippedCards.value.length === 2) {
      checkMatch()
    }
  }
}

const checkMatch = () => {
  const [first, second] = flippedCards.value

  if (first.card.image === second.card.image) {
    first.card.matched = true
    second.card.matched = true
  } else {
    setTimeout(() => {
      first.card.flipped = false
      second.card.flipped = false
    }, 800)
  }

  flippedCards.value = []
  checkGameWon()
}

// ⏯ Start game on component mount
resetGame()
</script>
