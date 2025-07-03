<template>
  <div
    class="bg-white rounded-2xl shadow-md w-[300px] px-6 py-6 text-center transition-transform duration-300 hover:scale-105 hover:shadow-lg"
  >
    <!-- Header -->
    <div class="bg-cardhead rounded-t-2xl py-4 px-2">
      <slot name="header">
        <h2 class="text-xl font-bold ">Default Title</h2>
      </slot>
    </div>

    <!-- Body -->
    <div class="py-4 text-sm ">
      <slot>
        <p>This is default card content. Replace it with your own!</p>
      </slot>
    </div>

    <!-- Footer -->
    <div class="mt-4">
      <slot name="footer">
        <button
           class="bg-button hover:text-purple-900 text-white font-header  px-4 py-2 rounded- hover:bg-purple-100 transition"
        >
          Learn More
        </button>
      </slot>
    </div>
  </div>
</template>

<script>
export default {
  name: "ChildFriendlyCard",
};
</script>
