import { createRouter, createWebHistory } from "vue-router";
import ChatView from "../views/ChatView.vue";
import NotFound from "../views/NotFound.vue";
import LoginView from "../views/LoginView.vue";
import useAuthStore from "../stores/auth";
import LoadingView from "../views/LoadingView.vue";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: "/",
      name: "loading",
      component: LoadingView,
    },
    {
      path: "/chat",
      name: "new-chat",
      redirect: "/chat/new",
    },
    {
      path: "/login",
      name: "login",
      component: LoginView,
    },
    {
      path: "/chat/:id",
      name: "chat",
      component: ChatView,
      meta: { requiresAuth: true },
    },
    {
      path: "/:pathMatch(.*)*",
      name: "not-found",
      component: NotFound,
    },
  ],
});

router.beforeEach(async (to, _, next) => {
  const authStore = useAuthStore();

  if (!authStore.adminChecked && to.name !== "loading") {
    next({ name: "loading" });
  }

  if (to.meta.requiresAuth && !authStore.isAdmin) {
    next({ name: "login" });
  } else {
    next();
  }
});

export default router;
