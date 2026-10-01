<template>
  <h1>Recommendations</h1>
  <p class="muted">Courses whose prerequisites you have already completed.</p>
  <div v-if="!list" class="muted">Loading…</div>
  <template v-else>
    <div class="grid2">
      <div v-for="c in list" :key="c.id" class="course static">
        <div class="row between"><span class="code">{{ c.id }}</span><span class="cr-pill">{{ c.credits }} credits</span></div>
        <div class="title">{{ c.name }}</div>
        <div class="note cap"><Info :size="15" /> {{ c.level }} · {{ c.kind }}</div>
      </div>
    </div>
    <p><RouterLink to="/planner" class="btn primary">Plan these courses</RouterLink></p>
  </template>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { RouterLink } from "vue-router";
import { Info } from "lucide-vue-next";
import { api } from "../api";

const list = ref(null);
onMounted(async () => { list.value = await api.recommendations(); });
</script>
