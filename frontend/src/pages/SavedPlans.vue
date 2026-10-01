<template>
  <h1>Saved Plans</h1>
  <div v-if="!plans" class="muted">Loading…</div>
  <template v-else>
    <div v-if="!plans.length" class="card">No plans yet. <RouterLink to="/planner">Create one</RouterLink>.</div>
    <div v-for="p in plans" :key="p.id" class="plan-block">
      <div class="row between">
        <div>
          <h3 class="plan-name">{{ p.name }}</h3>
          <span class="muted">{{ p.terms.length }} terms · {{ p.course_count }} courses · {{ p.total_credits }} credits</span>
        </div>
        <div class="row gap-s">
          <RouterLink :to="`/planner/${p.id}`" class="btn"><Pencil :size="16" /> Edit</RouterLink>
          <button class="btn danger" @click="remove(p.id)"><Trash2 :size="16" /> Delete</button>
        </div>
      </div>
      <PlanTerms :terms="p.terms" />
    </div>
  </template>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { Trash2, Pencil } from "lucide-vue-next";
import { api } from "../api";
import PlanTerms from "./PlanTerms.vue";

const emit = defineEmits(["changed"]);
const plans = ref(null);
async function load() { plans.value = await api.plans(); }
onMounted(load);

async function remove(id) {
  if (!confirm("Delete this plan?")) return;
  await api.deletePlan(id);
  await load();
  emit("changed");
}
</script>
