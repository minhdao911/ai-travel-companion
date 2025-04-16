import { createRouter, createWebHistory } from "vue-router";
import ChatView from "../views/ChatView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "home",
      redirect: "/chat/new",
    },
    {
      path: "/chat",
      name: "new-chat",
      redirect: "/chat/new",
    },
    {
      path: "/chat/:id",
      name: "chat",
      component: ChatView,
    },
  ],
});

export default router;
