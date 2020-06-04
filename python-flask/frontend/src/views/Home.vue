<template>
  <div class="home">
    <Wizardv2 />
    <!-- <img
      alt="Vue logo"
      src="../assets/logo.png"
    >
    <HelloWorld msg="Welcome to Your Vue.js App" /> -->
  </div>
</template>

<script>
// @ is an alias to /src
// import HelloWorld from '@/components/HelloWorld.vue'
import Wizardv2 from '@/components/Wizardv2.vue'
export default {
  name: 'Home',
  components: {
    // HelloWorld,
    Wizardv2
  }
}
</script>
