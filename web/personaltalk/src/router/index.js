import { createRouter, createWebHistory } from 'vue-router'
import PersonalTalkIndex from "@/views/PersonalTalkIndex.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'PersonalTalkIndex',
      component: PersonalTalkIndex,
    },
  ],
})

export default router
