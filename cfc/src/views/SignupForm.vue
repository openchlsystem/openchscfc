<template>
    <div class="signup-form">
        <h1>Welcome! 🌟</h1>
        <p>Let's get started on your adventure!</p>
        <form @submit.prevent="submitForm">
            <!-- Name -->
            <div class="form-group">
                <label for="name">What's your name? 😊</label>
                <input type="text" id="name" v-model="form.name" placeholder="Enter your first name" required />
            </div>

            <!-- Age -->
            <div class="form-group">
                <label for="age">How old are you? 🎂</label>
                <input type="number" id="age" v-model="form.age" placeholder="Enter your age" min="1" max="18"
                    required />
            </div>

            <!-- Gender -->
            <div class="form-group">
                <label for="gender">What's your gender? 🧒</label>
                <select id="gender" v-model="form.gender">
                    <option disabled value="">Select your gender</option>
                    <option value="boy">Boy</option>
                    <option value="girl">Girl</option>
                    <option value="other">Other</option>
                    <option value="prefer-not-to-say">Prefer not to say</option>
                </select>
            </div>

            <!-- Parent/Guardian Email -->
            <div class="form-group">
                <label for="parent-email">Parent/Guardian Email 📧</label>
                <input type="email" id="parent-email" v-model="form.parentEmail" placeholder="Enter your parent's email"
                    required />
            </div>

            <!-- Interests -->
            <div class="form-group">
                <label for="interests">What do you like? 🌈</label>
                <input type="text" id="interests" v-model="form.interests" placeholder="E.g., games, books, sports" />
            </div>

            <!-- Consent -->
            <div class="form-group">
                <label>
                    <input type="checkbox" v-model="form.consent" required />
                    I have my parent's/guardian's permission to sign up. ✅
                </label>
            </div>

            <!-- Submit Button -->
            <div class="form-group">
                <button type="submit" class="submit-button">Start 🚀</button>
            </div>
        </form>
    </div>
</template>

<script>
    export default {
        data() {
            return {
                form: {
                    name: "",
                    age: null,
                    gender: "",
                    parentEmail: "",
                    interests: "",
                    consent: false,
                },
            };
        },
        methods: {
            submitForm() {
                if (this.form.consent) {
                    alert(`Thank you, ${this.form.name}! You're all signed up! 🎉`);
                    // Handle the signup logic here (e.g., API call)
                } else {
                    alert("Please confirm you have your parent's/guardian's permission.");
                }
            },
        },
    };
</script>

<style scoped>
    .signup-form {
        max-width: 400px;
        margin: auto;
        padding: 20px;
        border: 2px solid #f4c2c2;
        border-radius: 10px;
        background-color: #fef9ef;
        text-align: center;
        font-family: "Comic Sans MS", cursive, sans-serif;
    }

    h1 {
        font-size: 24px;
        color: #ff6f61;
    }

    p {
        font-size: 16px;
        color: #333;
    }

    .form-group {
        margin-bottom: 15px;
        text-align: left;
    }

    label {
        display: block;
        font-size: 14px;
        color: #555;
        margin-bottom: 5px;
    }

    input,
    select,
    button {
        width: 100%;
        padding: 10px;
        font-size: 14px;
        border: 1px solid #ddd;
        border-radius: 5px;
    }

    button {
        background-color: #ff6f61;
        color: white;
        border: none;
        cursor: pointer;
    }

    button:hover {
        background-color: #e65c50;
    }
</style>
