<template>
  <div class="min-h-screen flex flex-col justify-center items-center bg-[#fff59d] p-6">
    <h1 class="text-4xl font-header font-bold text-darktext mb-2">Math Puzzle Game</h1>
    <p class="text-md text-darktext mb-4 font-text">Can you solve this one?</p>

    <div class="bg-white shadow-md rounded-xl p-6 w-full max-w-lg flex flex-col items-center gap-4">
      <p class="text-2xl text-black font-semibold">{{ currentProblem }}</p>
      <input
        v-model="userAnswer"
        type="number"
        class="w-full p-3 border border-gray-400 rounded-lg text-center"
        placeholder="Your answer"
        @change="checkAnswer"
        :disabled="isDisabled"
      />
      <button
        @click="generateProblem"
        class="bg-button text-white font-header px-4 py-2 rounded-md hover:text-purple-900 hover:bg-purple-100 transition w-full"
        :disabled="isDisabled"
      >
        Next Puzzle
      </button>
      <p v-if="resultMessage" class="text-green-600 font-medium">{{ resultMessage }}</p>
      <p class="text-sm font-text">Score: {{ score }}</p>
    </div>
  </div>
</template>




<script>
    import { ref } from "vue";

    export default {
        name: "MathPuzzleGame",
        setup() {
            const score = ref(0); // Reactive score
            const userAnswer = ref('');
            const resultMessage = ref('');
            const currentProblem = ref('');
            const correctAnswer = ref(0);
            const isDisabled = ref(false);

            const generateRandomNumber = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min;

            const generateProblem = () => {

                const num1 = generateRandomNumber(1, 10);
                const num2 = generateRandomNumber(1, 10);
                const operation = generateRandomNumber(1, 4); // 1: addition, 2: subtraction, 3: multiplication, 4: division

                if (operation === 1) {
                    currentProblem.value = `${num1} + ${num2}`;
                    correctAnswer.value = num1 + num2;
                } else if (operation === 2) {
                    currentProblem.value = `${num1} - ${num2}`;
                    correctAnswer.value = num1 - num2;
                } else if (operation === 3) {
                    currentProblem.value = `${num1} × ${num2}`;
                    correctAnswer.value = num1 * num2;
                } else if (operation === 4) {
                    currentProblem.value = `${num1} ÷ ${num2}`;
                    correctAnswer.value = num1 / num2;
                }

                userAnswer.value = '';
                resultMessage.value = '';
                isDisabled.value = false;
            };

            const checkAnswer = () => {
                if (parseInt(userAnswer.value) === correctAnswer.value) {
                    resultMessage.value = "Correct! Well done!";
                    score.value += 1; // Update the score correctly
                    console.log("Score:", score.value); // Check the score value
                } else {
                    resultMessage.value = `Oops! The correct answer was ${correctAnswer.value}.`;
                }
                isDisabled.value = true;
                setTimeout(generateProblem, 2000); // Generate new problem after 2 seconds
            };

            generateProblem(); // Initial problem generation

            return { score, userAnswer, resultMessage, currentProblem, generateProblem, checkAnswer, isDisabled };
        },
    };
</script>

<style scoped>
    
</style>
