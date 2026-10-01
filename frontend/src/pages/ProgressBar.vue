<template>
  <div>
    <div class="bar">
      <div v-if="completed > 0" class="seg green" :style="{ width: pct(completed) }">{{ completed }}</div>
      <div v-if="planned > 0" class="seg blue" :style="{ width: pct(planned) }">{{ planned }}</div>
      <div class="seg grey" style="flex:1">{{ remainingBar }}</div>
    </div>
    <div class="legend">
      <span class="chip green"><i /> Completed: {{ completed }}</span>
      <span class="chip blue"><i /> Planned: {{ planned }}</span>
      <span class="chip grey"><i /> Remaining: {{ total - completed }}</span>
      <b class="right">{{ completed }} / {{ total }} credits</b>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";
const props = defineProps({ completed: { type: Number, required: true }, planned: { type: Number, default: 0 }, total: { type: Number, required: true } });
const remainingBar = computed(() => Math.max(props.total - props.completed - props.planned, 0));
function pct(n) { return `${(n / props.total) * 100}%`; }
</script>
