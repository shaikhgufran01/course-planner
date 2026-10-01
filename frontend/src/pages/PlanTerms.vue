<template>
  <div class="term-grid">
    <div v-for="(t, i) in terms" :key="t.label + i" class="term-card" :style="{ borderColor: palette(i).main }">
      <div class="term-head" :style="{ background: palette(i).main }">
        <div class="term-title">{{ t.label }}</div>
        <div class="term-sub" :style="{ color: palette(i).sub }">{{ credits(t) }} credits • {{ t.courses.length }} courses</div>
      </div>
      <div class="term-body">
        <div v-for="(c, j) in t.courses" :key="c.id" class="term-row">
          <span class="num" :style="{ background: palette(i).main, color: palette(i).fg }">{{ j + 1 }}</span>
          <div class="term-name">
            <div>{{ c.name }}</div>
            <div class="term-code" :style="{ color: palette(i).code }">{{ c.id }}</div>
          </div>
          <span class="cr" :style="{ background: palette(i).main, color: palette(i).fg }">{{ c.credits }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { PALETTE } from "./palette.js";
defineProps({ terms: { type: Array, required: true } });
function palette(i) { return PALETTE[i % PALETTE.length]; }
function credits(t) { return t.courses.reduce((n, c) => n + c.credits, 0); }
</script>
