<template>
  <div class="min-h-screen flex flex-col justify-center items-center bg-[#fff59d] p-6 pt-40">
    <h1 class="text-4xl font-header font-bold text-darktext mb-2">Coloring Fun!</h1>
    <p class="text-md text-darktext mb-4 font-text text-center">
      Pick a color and tap on the shapes below to color them!
    </p>

    <!-- Game Box -->
    <div class="bg-white shadow-md rounded-xl p-6 w-full max-w-lg flex flex-col items-center gap-4">
      <!-- Color Palette -->
      <div class="flex flex-wrap justify-center gap-2">
        <div
          v-for="color in colors"
          :key="color"
          :style="{ backgroundColor: color }"
          class="w-8 h-8 rounded-full border-2 border-gray-200 cursor-pointer"
          @click="selectedColor = color"
        ></div>
      </div>

      <!-- Shapes -->
      <div class="grid grid-cols-3 gap-4 mt-4">
        <div
          v-for="(shape, index) in shapes"
          :key="index"
          :style="{
            backgroundColor: shape.color,
            width: shape.size,
            height: shape.size,
            borderRadius: shape.type === 'circle' ? '50%' : '0',
            border: '2px solid #fff'
          }"
          @click="colorShape(index)"
          class="cursor-pointer shadow-md"
        ></div>
      </div>

      <!-- Selected Color -->
      <p v-if="selectedColor" class="text-sm font-text text-center">
        You selected:
        <span :style="{ color: selectedColor }" class="font-bold">{{ selectedColor }}</span>
      </p>
    </div>
  </div>
</template>

<script>
    import { ref } from 'vue';

    export default {
        name: 'ColoringFun',
        setup() {
            const colors = ['#ff7043', '#ffeb3b', '#4caf50', '#2196f3', '#9c27b0', '#ff4081'];
            const selectedColor = ref('');
            const shapes = ref([
                { type: 'square', color: '#f1f1f1', size: '100px' },
                { type: 'circle', color: '#f1f1f1', size: '100px' },
                { type: 'square', color: '#f1f1f1', size: '150px' },
                { type: 'circle', color: '#f1f1f1', size: '150px' },
            ]);

            const colorShape = (index) => {
                if (!selectedColor.value) {
                    alert('Please select a color first!');
                    return;
                }
                shapes.value[index].color = selectedColor.value;
            };

            return {
                colors,
                selectedColor,
                shapes,
                colorShape,
            };
        },
    };
</script>


