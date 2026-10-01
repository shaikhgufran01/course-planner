<template>
  <div class="row between top">
    <div>
      <div class="welcome">Welcome</div>
      <div v-if="editing" class="row gap">
        <input class="input" v-model="name" autofocus @keydown.enter="save" />
        <button class="btn primary" @click="save">Save</button>
      </div>
      <h1 v-else class="name">
        {{ student.name.toUpperCase() }}
        <button class="link" title="Edit name" @click="name = student.name; editing = true"><Pencil :size="16" /></button>
      </h1>
      <div class="muted">{{ student.program }}</div>
      <span class="pill green">{{ student.status }}</span>
    </div>
    <div class="right-col">
      <div class="row gap-s muted term-now">
        <span class="icon-sq sm blue"><CalendarDays :size="18" /></span>
        <span>Current Term: <b>{{ student.current_term }}</b> ({{ student.current_term_code }})</span>
      </div>
      <RouterLink to="/planner" class="btn primary wide">
        <span class="icon-sq xs light"><CalendarPlus :size="16" /></span> Plan Your Courses
      </RouterLink>
    </div>
  </div>

  <div class="grid3">
    <div class="card stat">
      <div><div class="muted">Current Level</div><div class="big">{{ student.level.toUpperCase() }}</div><div class="muted">{{ student.program }}</div></div>
      <span class="icon-sq blue"><Award :size="26" /></span>
    </div>
    <div class="card stat">
      <div><div class="muted">Credits Earned</div><div class="big">{{ student.completed_credits }}</div><div class="muted">{{ student.remaining_credits }} credits remaining for BS</div></div>
      <span class="icon-sq green"><BookOpen :size="26" /></span>
    </div>
    <div class="card stat">
      <div><div class="muted">Total Terms</div><div class="big">{{ student.total_terms }}</div><div class="muted">In program since {{ student.start_term }}</div></div>
      <span class="icon-sq orange"><CalendarDays :size="26" /></span>
    </div>
  </div>

  <div class="card flush">
    <div class="card-head grey"><b>Your Progress</b></div>
    <div class="pad"><ProgressBar :completed="student.completed_credits" :planned="student.planned_credits" :total="student.total_credits" /></div>
  </div>
  <p class="muted small">Tip: mark the courses you've already finished in <RouterLink to="/tracker">Credit Progress Tracker</RouterLink>.</p>
</template>

<script setup>
import { ref } from "vue";
import { RouterLink } from "vue-router";
import { Award, BookOpen, CalendarDays, CalendarPlus, Pencil } from "lucide-vue-next";
import { api } from "../api";
import ProgressBar from "./ProgressBar.vue";

const props = defineProps({ student: { type: Object, required: true } });
const emit = defineEmits(["changed"]);
const editing = ref(false);
const name = ref(props.student.name);

async function save() {
  if (name.value.trim()) { await api.updateName(name.value.trim()); emit("changed"); }
  editing.value = false;
}
</script>
