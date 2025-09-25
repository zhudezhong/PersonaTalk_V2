import { createRouter, createWebHistory } from 'vue-router'
import PersonalTalkIndex from "@/views/PersonalTalkIndex.vue";
import SpokenDialogue from "@/views/SpokenDialogue.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'PersonalTalkIndex',
      component: PersonalTalkIndex,
    },{
      path: '/SpokenDialogue',
      name: 'SpokenDialogue',
      component: SpokenDialogue,
    }
  ],
})

export default router
