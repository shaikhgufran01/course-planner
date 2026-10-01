<template>
  <div class="row gap wrap title-row">
    <h1>Credit Progress Tracker</h1>
    <span class="pill blue">{{ completedCount }} / {{ totalCount }} courses done</span>
  </div>

  <div v-if="!progress" class="muted">Loading…</div>
  <template v-else>
    <!-- Progress overview -->
    <div class="card flush">
      <div class="card-head"><span class="icon-sq blue"><TrendingUp :size="22" /></span><b>Overall Progress</b></div>
      <div class="pad">
        <ProgressBar :completed="progress.completed_credits" :total="progress.total_credits" />
        <div class="grid3 mt">
          <div v-for="(v, lvl) in progress.by_level" :key="lvl" class="tile blue">
            <div class="cap level-label">{{ lvl }}</div>
            <b>{{ v.completed_credits }} / {{ v.total_credits }} credits</b>
          </div>
        </div>
      </div>
    </div>

    <!-- Search and filter bar -->
    <div class="filter-bar">
      <div class="search-wrap">
        <Search :size="18" class="search-icon" />
        <input class="search-input" v-model="search" placeholder="Search courses by ID or name…" />
        <button v-if="search" class="search-clear" @click="search = ''"><X :size="16" /></button>
      </div>
      <div class="filter-pills">
        <button v-for="f in FILTERS" :key="f.key" class="filter-pill" :class="{ active: filter === f.key }" @click="filter = f.key">
          {{ f.label }}
          <span class="filter-count">{{ countFor(f.key) }}</span>
        </button>
      </div>
    </div>

    <!-- Grouped courses -->
    <section v-for="lvl in LEVELS" :key="lvl" class="card flush level-section" v-show="filteredFor(lvl).length">
      <div class="card-head grey">
        <span class="icon-sq" :class="LEVEL_COLORS[lvl]"><component :is="LEVEL_ICONS[lvl]" :size="22" /></span>
        <b class="cap big-h">{{ LEVEL_LABELS[lvl] || lvl }}</b>
        <span class="items-badge">{{ doneFor(lvl) }} / {{ filteredFor(lvl).length }} completed</span>
        <span class="grow" />
        <button class="link level-toggle" @click="toggleLevel(lvl)">
          <component :is="openLevels[lvl] ? ChevronUp : ChevronDown" :size="20" />
        </button>
      </div>
      <div v-show="openLevels[lvl]" class="pad">
        <!-- Sub-group by kind -->
        <div v-for="kind in ['theory', 'project', 'exam']" :key="kind" v-show="kindList(lvl, kind).length" class="kind-group">
          <div class="kind-header">
            <component :is="kind === 'theory' ? BookOpen : Briefcase" :size="18" class="kind-icon" />
            <span class="cap kind-title">{{ kind }} Courses</span>
            <span class="kind-count">{{ kindList(lvl, kind).length }}</span>
          </div>
          <div class="course-grid">
            <div v-for="c in kindList(lvl, kind)" :key="c.id" class="tracker-card"
                 :class="{ done: c.completed, toggling: toggling === c.id }" @click="toggle(c)">
              <div class="tracker-top">
                <span class="tracker-code">{{ c.id }}</span>
                <span class="cr-pill">{{ c.credits }} cr</span>
              </div>
              <div class="tracker-name">{{ c.name }}</div>
              <div class="tracker-bottom">
                <div class="tracker-check">
                  <span class="checkbox" :class="{ checked: c.completed }">
                    <Check v-if="c.completed" :size="14" />
                  </span>
                  <span class="check-label">{{ c.completed ? 'Completed' : 'Mark complete' }}</span>
                </div>
                <span v-if="c.prerequisites.length" class="prereq-hint">
                  <Info :size="14" /> {{ c.prerequisites.length }} prereq{{ c.prerequisites.length > 1 ? 's' : '' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <div v-if="noResults" class="card muted" style="text-align:center;padding:40px">
      No courses match your search.
    </div>
  </template>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { BookOpen, Briefcase, Check, ChevronDown, ChevronUp, GraduationCap, Info, Layers, Search, TrendingUp, X } from "lucide-vue-next";
import { api } from "../api";
import ProgressBar from "./ProgressBar.vue";

const emit = defineEmits(["changed"]);

const LEVELS = ["degree", "l4_degree", "l5_degree", "gate"];
const LEVEL_COLORS = { degree: "blue", l4_degree: "orange", l5_degree: "green", gate: "blue" };
const LEVEL_ICONS = { degree: BookOpen, l4_degree: Layers, l5_degree: GraduationCap, gate: GraduationCap };
const LEVEL_LABELS = { degree: "Degree", l4_degree: "L4 Degree", l5_degree: "L5 Degree", gate: "GATE" };
const FILTERS = [
  { key: "all", label: "All" },
  { key: "pending", label: "Pending" },
  { key: "done", label: "Done" },
];

const courses = ref([]);
const progress = ref(null);
const search = ref("");
const filter = ref("all");
const toggling = ref(null);
const openLevels = ref({ foundation: true, diploma: true, degree: true });

async function load() {
  const [c, p] = await Promise.all([api.courses(), api.progress()]);
  courses.value = c;
  progress.value = p;
}
onMounted(load);

function toggleLevel(lvl) { openLevels.value = { ...openLevels.value, [lvl]: !openLevels.value[lvl] }; }

// Filtering
function matches(c) {
  const q = search.value.toLowerCase();
  if (q && !c.id.toLowerCase().includes(q) && !c.name.toLowerCase().includes(q)) return false;
  if (filter.value === "done" && !c.completed) return false;
  if (filter.value === "pending" && c.completed) return false;
  return true;
}

const filtered = computed(() => courses.value.filter(matches));
function filteredFor(lvl) { return filtered.value.filter((c) => c.level === lvl); }
function kindList(lvl, kind) { return filteredFor(lvl).filter((c) => c.kind === kind); }
function doneFor(lvl) { return filteredFor(lvl).filter((c) => c.completed).length; }
const noResults = computed(() => filtered.value.length === 0 && (search.value || filter.value !== "all"));

const completedCount = computed(() => courses.value.filter((c) => c.completed).length);
const totalCount = computed(() => courses.value.length);

function countFor(key) {
  if (key === "all") return courses.value.length;
  if (key === "done") return courses.value.filter((c) => c.completed).length;
  return courses.value.filter((c) => !c.completed).length;
}

async function toggle(c) {
  toggling.value = c.id;
  try {
    await (c.completed ? api.uncomplete(c.id) : api.complete(c.id));
    await load();
    emit("changed");
  } finally {
    toggling.value = null;
  }
}
</script>

<style scoped>
/* Filter bar */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  margin: 12px 0 4px;
  flex-wrap: wrap;
}
.search-wrap {
  position: relative;
  flex: 1;
  min-width: 220px;
  max-width: 420px;
}
.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--muted);
  pointer-events: none;
}
.search-input {
  width: 100%;
  padding: 10px 38px 10px 42px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font: inherit;
  background: var(--card);
  transition: border-color 0.2s;
}
.search-input:focus {
  outline: none;
  border-color: var(--blue);
  box-shadow: 0 0 0 3px rgba(37,99,235,.12);
}
.search-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--muted);
  padding: 2px;
  display: flex;
}
.filter-pills {
  display: flex;
  gap: 8px;
}
.filter-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1.5px solid var(--border);
  background: var(--card);
  cursor: pointer;
  font: inherit;
  font-weight: 600;
  font-size: 14px;
  color: var(--muted);
  transition: all 0.15s;
}
.filter-pill.active {
  background: var(--blue);
  color: #fff;
  border-color: var(--blue);
}
.filter-pill:hover:not(.active) {
  border-color: var(--blue);
  color: var(--blue);
}
.filter-count {
  background: rgba(0,0,0,.08);
  border-radius: 999px;
  padding: 1px 8px;
  font-size: 12px;
  font-weight: 700;
}
.filter-pill.active .filter-count {
  background: rgba(255,255,255,.25);
}

/* Level sections */
.level-section { margin-top: 16px; }
.level-label { font-weight: 600; margin-bottom: 2px; }
.level-toggle {
  display: flex;
  align-items: center;
  color: var(--muted);
}

/* Kind groups */
.kind-group { margin-bottom: 24px; }
.kind-group:last-child { margin-bottom: 0; }
.kind-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}
.kind-icon { color: var(--blue); }
.kind-title { font-size: 17px; font-weight: 600; color: #374151; }
.kind-count {
  background: var(--blue);
  color: #fff;
  border-radius: 999px;
  min-width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

/* Course cards */
.course-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 14px;
}
.tracker-card {
  border: 2px solid var(--border);
  border-radius: 14px;
  padding: 18px;
  background: var(--card);
  cursor: pointer;
  transition: all 0.18s ease;
  position: relative;
  user-select: none;
}
.tracker-card:hover {
  border-color: #93b4ff;
  box-shadow: 0 2px 12px rgba(37,99,235,.1);
  transform: translateY(-1px);
}
.tracker-card.done {
  border-color: var(--green);
  background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
}
.tracker-card.done:hover {
  border-color: #15803d;
  box-shadow: 0 2px 12px rgba(22,163,74,.12);
}
.tracker-card.toggling {
  opacity: 0.6;
  pointer-events: none;
}

.tracker-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.tracker-code {
  color: var(--blue);
  font-weight: 700;
  font-size: 14px;
}
.tracker-card.done .tracker-code {
  color: var(--green);
}
.tracker-name {
  font-weight: 700;
  font-size: 16px;
  line-height: 1.3;
  margin-bottom: 12px;
  color: var(--text);
}
.tracker-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Custom checkbox */
.tracker-check {
  display: flex;
  align-items: center;
  gap: 8px;
}
.checkbox {
  width: 22px;
  height: 22px;
  border-radius: 6px;
  border: 2px solid #d1d5db;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s;
  flex-shrink: 0;
}
.checkbox.checked {
  background: var(--green);
  border-color: var(--green);
  color: #fff;
}
.check-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--muted);
}
.tracker-card.done .check-label {
  color: var(--green);
}
.prereq-hint {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--muted);
}

/* Responsive */
@media (max-width: 700px) {
  .course-grid { grid-template-columns: 1fr; }
  .filter-bar { flex-direction: column; align-items: stretch; }
  .search-wrap { max-width: 100%; }
}
</style>
