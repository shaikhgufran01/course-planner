import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import Dashboard from "./pages/Dashboard.vue";
import Planner from "./pages/Planner.vue";
import SavedPlans from "./pages/SavedPlans.vue";

import CreditTracker from "./pages/CreditTracker.vue";
import "./styles.css";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/", component: Dashboard },
    { path: "/planner", component: Planner },
    { path: "/planner/:id", component: Planner, props: true },
    { path: "/plans", component: SavedPlans },

    { path: "/tracker", component: CreditTracker },
  ],
});

createApp(App).use(router).mount("#app");
