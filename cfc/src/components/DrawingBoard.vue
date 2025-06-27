<template>
  <div class="flex flex-col gap-4 justify-center items-center w-full">
    <h2 class="font-header font-bold text-subtitle text-xl">Draw Your Feelings</h2>

    <!-- Smaller, fixed-size responsive wrapper -->
    <div class="w-full max-w-[400px] aspect-[4/3] bg-white rounded-lg shadow-inner relative">
      <canvas
        ref="drawingCanvas"
        class="absolute top-0 left-0 w-full h-full rounded-lg"
        @mousedown="startDrawing"
        @mousemove="draw"
        @mouseup="stopDrawing"
        @mouseleave="stopDrawing"
        @touchstart="startDrawing"
        @touchmove="draw"
        @touchend="stopDrawing"
      ></canvas>
    </div>

    <div class="flex gap-4 justify-center items-center flex-wrap">
      <button class="bg-button rounded-lg text-white font-header px-4 py-2" @click="clearCanvas">
        Clear Drawing
      </button>
      <button class="bg-button rounded-lg text-white font-header px-4 py-2" @click="saveDrawing">
        Save Drawing
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'

export default {
  name: 'DrawingBoard',
  setup() {
    const drawingCanvas = ref(null)
    const isDrawing = ref(false)
    let ctx = null

    const resizeCanvas = () => {
      const canvas = drawingCanvas.value
      const container = canvas.parentElement

      canvas.width = container.offsetWidth
      canvas.height = container.offsetHeight

      ctx = canvas.getContext('2d')
      ctx.lineWidth = 2
      ctx.lineCap = 'round'
      ctx.strokeStyle = '#000'
    }

    onMounted(() => {
      nextTick(() => {
        resizeCanvas()
        window.addEventListener('resize', resizeCanvas)
      })
    })

    const startDrawing = (event) => {
      isDrawing.value = true
      const { offsetX, offsetY } = getEventCoordinates(event)
      ctx.beginPath()
      ctx.moveTo(offsetX, offsetY)
    }

    const draw = (event) => {
      if (!isDrawing.value) return
      const { offsetX, offsetY } = getEventCoordinates(event)
      ctx.lineTo(offsetX, offsetY)
      ctx.stroke()
    }

    const stopDrawing = () => {
      isDrawing.value = false
      ctx.closePath()
    }

    const clearCanvas = () => {
      const canvas = drawingCanvas.value
      ctx.clearRect(0, 0, canvas.width, canvas.height)
    }

    const saveDrawing = () => {
      const canvas = drawingCanvas.value
      const dataURL = canvas.toDataURL('image/png')
      const link = document.createElement('a')
      link.href = dataURL
      link.download = 'drawing.png'
      link.click()
    }

    const getEventCoordinates = (event) => {
      const canvas = drawingCanvas.value
      const rect = canvas.getBoundingClientRect()
      if (event.touches && event.touches[0]) {
        return {
          offsetX: event.touches[0].clientX - rect.left,
          offsetY: event.touches[0].clientY - rect.top,
        }
      }
      return {
        offsetX: event.clientX - rect.left,
        offsetY: event.clientY - rect.top,
      }
    }

    return {
      drawingCanvas,
      startDrawing,
      draw,
      stopDrawing,
      clearCanvas,
      saveDrawing,
    }
  },
}
</script>

<style scoped>
canvas {
  touch-action: none;
}
</style>
