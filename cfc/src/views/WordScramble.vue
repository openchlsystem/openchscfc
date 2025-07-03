<template>
  <div class="min-h-screen flex flex-col justify-center items-center bg-[#fff59d] p-6">
    <h1 class="text-4xl font-header font-bold text-black mb-2">Word Scramble</h1>
    <p class="text-md text-darktext mb-4 font-text text-center">
      Unscramble the letters to form the word!
    </p>

    <div class="bg-white shadow-md rounded-xl p-6 w-full max-w-lg flex flex-col items-center gap-4">
      <p class="text-2xl text-black font-semibold font-header tracking-widest">{{ scrambledWord }}</p>

      <input
        v-model="userGuess"
        class="w-full p-3 border border-gray-400 rounded-lg text-center"
        type="text"
        placeholder="Enter your guess"
        @change="checkGuess"
      />

      <button
        class="bg-button text-white font-header px-4 py-2 rounded-md hover:text-purple-900 hover:bg-purple-100 transition w-full"
        @click="scrambleWord"
      >
        Next Word
      </button>

      <p v-if="resultMessage" class="text-green-600 font-medium">{{ resultMessage }}</p>
      <p class="text-sm font-text">Score: {{ score }}</p>
    </div>
  </div>
</template>


<script>
    import { ref } from 'vue';

    export default {
        name: 'WordScramble',
        setup() {
            const words = [
                'apple', 'banana', 'cherry', 'grape', 'orange', 'melon', 'kiwi', 'lemon', 'mango', 'peach',
                'plum', 'pear', 'watermelon', 'pineapple', 'strawberry', 'blueberry', 'coconut', 'apricot', 'lime', 'applesauce',
                'grapefruit', 'pomegranate', 'kiwifruit', 'blueberry', 'raspberry', 'blackberry', 'cantaloupe', 'papaya', 'fruitcake', 'carrot'
            ];
            const score = ref(0);
            const scrambledWord = ref('');
            const userGuess = ref('');
            const resultMessage = ref('');

            const scrambleWord = () => {
                const randomWord = words[Math.floor(Math.random() * words.length)];
                scrambledWord.value = randomWord.split('').sort(() => Math.random() - 0.5).join('');
                userGuess.value = '';
                resultMessage.value = '';
            };

            const checkGuess = () => {
                const word = scrambledWord.value.split('').sort().join('');
                if (userGuess.value.toLowerCase().split('').sort().join('') === word) {
                    score.value++;
                    resultMessage.value = 'Correct! 🎉';
                    scrambleWord();
                } else {
                    resultMessage.value = 'Oops! Try again! 😅';
                }
            };

            // Initialize the game with the first scrambled word
            scrambleWord();

            return {
                score,
                scrambledWord,
                userGuess,
                resultMessage,
                scrambleWord,
                checkGuess,
            };
        },
    };
</script>


