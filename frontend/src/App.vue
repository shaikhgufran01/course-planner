<template>
  <div v-if="error" class="page"><div class="alert error">Could not reach the API: {{ error }}</div></div>
  <div v-else-if="!student" class="page muted">Loading…</div>
  <div v-else class="layout">
    <aside class="sidebar">
      <div v-for="section in NAV" :key="section.title">
        <div class="nav-section">{{ section.title }}</div>
        <RouterLink v-for="l in section.links" :key="l.to" :to="l.to" class="nav-link"
                    :class="{ active: isActive(l.to) }">
          <component :is="l.icon" :size="18" /> {{ l.label }}
        </RouterLink>
      </div>
      <div class="beta">
        <div><b>Beta:</b> This app is under beta testing. If you are facing any issues, please let the developer know.</div>
        <div class="btn report"><Bug :size="16" /> Report an Issue</div>
      </div>
    </aside>
    <main class="page">
      <RouterView :student="student" @changed="refresh" />
    </main>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import { Bug, CalendarCheck, Layers, LayoutGrid, TrendingUp } from "lucide-vue-next";
import { api } from "./api";

const NAV = [
  { title: "MAIN", links: [{ to: "/", label: "Dashboard", icon: LayoutGrid }] },

  { title: "PLANNER", links: [
    { to: "/planner", label: "Course Planner", icon: CalendarCheck },
    { to: "/plans", label: "Saved Plans", icon: Layers },
  ] },
  { title: "PROGRESS", links: [{ to: "/tracker", label: "Credit Progress Tracker", icon: TrendingUp }] },
];

const route = useRoute();
const student = ref(null);
const error = ref("");

function isActive(to) {
  return to === "/" ? route.path === "/" : route.path === to;
}

async function refresh() {
  try { student.value = await api.student(); }
  catch (e) { error.value = e.message; }
}
onMounted(refresh);
</script>
