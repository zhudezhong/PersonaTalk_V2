<script setup lang="ts">

import PersonalCard from "@/components/PersonalCard.vue";
</script>

<template>
  <div class="container">
    <PersonalCard/>
    <PersonalCard/>
    <PersonalCard/>
  </div>

</template>

<style scoped>
.container {
  margin: 100px auto;
  width: 650px;
  height: 600px;
  display: flex;
  justify-content: space-around;
  align-items: center;
}
</style>
