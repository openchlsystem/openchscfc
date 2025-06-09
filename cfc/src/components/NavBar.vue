<template>
    <nav >            
            <!-- Navigation Links -->
            <div class="flex justify-between" >
                 <!-- Home Icon -->
                <div>
                    <button  @click="navigateBack"><i class="bi bi-arrow-left"></i> Back</button>
                </div>
                <ul class="flex justify-between gap-4 items-center px-4 capitalize">
                    <li>home page</li>
                    <li ><a class="" href="#features">feelings hub</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#contact">Contact us</a></li>
                    <li><a href="#support">leaderboard</a></li>
                    <button class="border p-2 capitalize">send</button>
                    <button class="border p-2 capitalize bg-black text-white">submit</button>
                </ul>
            </div> 
    </nav>

</template>

<script>
    import { ref } from "vue";
    import { useRouter } from "vue-router";

    export default {
        setup() {
            const isMenuOpen = ref(false);
            const router = useRouter();

            const toggleMenu = () => {
                isMenuOpen.value = !isMenuOpen.value;
            };

            const navigateHome = () => {
                router.push("/");
            };

            const navigateBack = () => {
                router.back();
            };

            return {
                isMenuOpen,
                toggleMenu,
                navigateHome,
                navigateBack,
            };
        },
    };
</script>
