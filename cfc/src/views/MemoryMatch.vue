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
            class="w-full h-full object-cover rounded-lg"
          />
          <!-- Show Back if Not Flipped -->
          <img
            v-else
            src="https://via.placeholder.com/100x100.png?text=?"
            alt="Card back"
            class="w-full h-full object-cover rounded-lg"
          />
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



<script>
    import { ref, computed } from "vue";

    export default {
        setup() {
            const cards = ref([
                { image: 'https://via.placeholder.com/100x100.png?text=🍎', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍎', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍌', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍌', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍉', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍉', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍇', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍇', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍒', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍒', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍍', flipped: false, matched: false },
                { image: 'https://via.placeholder.com/100x100.png?text=🍍', flipped: false, matched: false },
            ]);
            const flippedCards = ref([]);
            const gameWon = ref(false);
            const gameStarted = ref(false);

            const shuffledCards = computed(() => {
                return [...cards.value].sort(() => Math.random() - 0.5);
            });

            const flipCard = (card, index) => {
                if (flippedCards.value.length < 2 && !card.flipped && !card.matched) {
                    card.flipped = true;
                    flippedCards.value.push({ card, index });

                    if (flippedCards.value.length === 2) {
                        checkMatch();
                    }
                }
            };

            const checkMatch = () => {
                const [firstCard, secondCard] = flippedCards.value;

                if (firstCard.card.image === secondCard.card.image) {
                    firstCard.card.matched = true;
                    secondCard.card.matched = true;
                } else {
                    setTimeout(() => {
                        firstCard.card.flipped = false;
                        secondCard.card.flipped = false;
                    }, 1000);
                }

                flippedCards.value = [];
                checkGameWon();
            };

            const checkGameWon = () => {
                gameWon.value = cards.value.every(card => card.matched);
            };

            const resetGame = () => {
                cards.value.forEach(card => {
                    card.flipped = false;
                    card.matched = false;
                });
                flippedCards.value = [];
                gameWon.value = false;
                gameStarted.value = false;
            };

            const startGame = () => {
                gameStarted.value = true;
            };

            return {
                shuffledCards,
                gameWon,
                gameStarted,
                flipCard,
                resetGame,
                startGame,
            };
        },
    };
</script>


