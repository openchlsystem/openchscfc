<template>
  <div class="py-20 px-16 flex flex-col gap-20">
    <div class="flex justify-between items-start ">
      <h1 class="font-extrabold font-header text-5xl w-3/7">Welcome to Your Safe Space for Feelings</h1>
      <div class="flex flex-col gap-8 w-3/7 ">
        <p class="text-lg">
          Here, children can explore their emotions in a fun and engaging way. Our vibrant interface
          and friendly design make it easy to express feelings and connect with others.
        </p>
        <div class="flex justify-start items-start gap-4">
          <button class="capitalize px-4 py-2 bg-black text-white">talk to us</button>
          <button class="capitalize px-4 py-2 border">learn more</button>
        </div>
      </div>
    </div>

    <div class="">
      <img
        src="https://imgs.search.brave.com/a4ZTHrZwdH2-zrSmfFM1xODUI-_3QOACAWowJLbsExo/rs:fit:500:0:0:0/g:ce/aHR0cHM6Ly9tZWRp/YS5pc3RvY2twaG90/by5jb20vaWQvOTUw/NjA1MDQ2L3Bob3Rv/L211bHRpZXRobmlj/LWNoaWxkcmVuLWlu/LWEtY2lyY2xlLmpw/Zz9zPTYxMng2MTIm/dz0wJms9MjAmYz1I/YXd6V0g4ZkJ6c0pT/dXp2aXV1UzNpUmhS/UEF3RVcyUE9RVExR/M0x6VWZZPQ"
        alt="Happy children illustration"
        class="w-full h-[738px] rounded-4xl object-cover"
      />
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()
    const navigateToStart = () => {
      window.location.replace('/safe-sharing')
    }

    return {
      navigateToStart,
    }
  },
}
</script>
