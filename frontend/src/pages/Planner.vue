<template>
  <div class="row gap wrap title-row">
    <h1>{{ step === 1 ? selectedLabels[active] + " Planning" : "Your Plan" }} <span v-if="step === 1" class="term-n">(Term {{ active + 1 }})</span></h1>
    <span class="pill blue">Step {{ step }} of 3</span>
    <span class="muted step-text">{{ heading }}</span>
    <span class="pill orange"><Info :size="16" /> Max {{ max }} courses per term</span>
  </div>

  <div class="card flush">
    <div class="card-head"><span class="icon-sq blue"><LineChart :size="22" /></span><b>Your Progress</b></div>
    <div class="pad"><ProgressBar :completed="student.completed_credits" :planned="plannedCredits" :total="student.total_credits" /></div>
  </div>

  <div v-if="step === 1" class="tabs">
    <button v-for="(t, i) in terms" :key="i" @click="active = i" class="tab" :class="{ on: i === active }"
            :style="i === active ? { borderColor: PALETTE[i % PALETTE.length].main } : {}">
      <span class="tab-dot" :style="{ background: PALETTE[i % PALETTE.length].main }" />
      <b>Term {{ i + 1 }}</b> · {{ selectedLabels[i] }} <span class="muted">({{ t.length }}/{{ max }})</span>
    </button>
    <button v-if="terms.length < allTerms.length" class="tab add" @click="addTerm"><Plus :size="16" /> Add term</button>
    <button v-if="terms.length > 1" class="link small" @click="removeLastTerm">Remove last term</button>
  </div>

  <!-- Term selector dropdown – shown in step 1 -->
  <div v-if="step === 1" class="term-selector-row">
    <label class="term-selector-label">Select term for <b>Term {{ active + 1 }}</b>:</label>
    <select class="term-select" :value="selectedLabels[active]" @change="onTermSelect($event)">
      <option v-for="t in availableTermOptions" :key="t" :value="t" :disabled="usedLabels.has(t) && t !== selectedLabels[active]">
        {{ t }} {{ usedLabels.has(t) && t !== selectedLabels[active] ? '(already used)' : '' }}
      </option>
    </select>
  </div>

  <div v-if="error" class="alert error">{{ error }}</div>

  <div class="split">
    <div>
      <template v-if="step === 1">
        <section v-for="lvl in LEVELS" :key="lvl" class="card flush" v-show="itemsFor(lvl).length">
          <div class="card-head grey"><b class="cap big-h">{{ LEVEL_LABELS[lvl] || lvl }}</b><span class="items-badge">{{ itemsFor(lvl).length }} items</span></div>
          <div class="pad">
            <div v-for="kind in ['theory', 'project', 'exam']" :key="kind" v-show="listFor(lvl, kind).length" class="group">
              <button class="group-head" @click="toggleOpen(lvl, kind)">
                <span class="icon-sq blue"><component :is="kind === 'theory' ? BookOpen : Briefcase" :size="22" /></span>
                <span class="cap group-title">{{ kind }} Courses</span>
                <span class="count-badge">{{ listFor(lvl, kind).length }}</span>
                <span class="grow" />
                <component :is="isOpen(lvl, kind) ? ChevronUp : ChevronDown" :size="20" />
              </button>
              <div v-show="isOpen(lvl, kind)" class="grid2 group-body">
                <button v-for="c in listFor(lvl, kind)" :key="c.id" @click="toggle(c)"
                        :disabled="['done','locked','other'].includes(statusOf(c).state)"
                        class="course" :class="statusOf(c).state">
                  <div class="row between">
                    <span class="code">{{ c.id }}</span>
                    <span class="cr-pill">{{ c.credits }} credits</span>
                  </div>
                  <div class="title">{{ c.name }}</div>
                  <div class="note">
                    <Info :size="15" />
                    {{ statusOf(c).note ?? (c.prerequisites.length ? `Prerequisites: ${c.prerequisites.join(", ")}` : "No prerequisites") }}
                  </div>
                </button>
              </div>
            </div>
          </div>
        </section>
      </template>

      <PlanTerms v-else-if="step === 2" :terms="terms.map((_, i) => ({ label: selectedLabels[i], courses: termCourses(i) }))" />

      <div v-else class="card">
        <h3>Plan name</h3>
        <input class="input" v-model="name" placeholder="e.g. My 3-term plan" autofocus />
      </div>
    </div>

    <aside class="card flush sticky">
      <div class="card-head grey"><span class="icon-sq blue"><ClipboardList :size="22" /></span><b class="big-h">Selection Summary</b></div>
      <div class="pad">
        <div class="grid2">
          <div class="tile blue"><div class="big">{{ activeCourses.length }}<span class="muted small"> / {{ max }}</span></div>Courses</div>
          <div class="tile red"><div class="big">{{ projects }}</div>Projects</div>
        </div>
        <h5>CREDITS BREAKDOWN</h5>
        <div class="row between line"><span>{{ selectedLabels[active] }}</span><b>{{ activeCredits }}</b></div>
        <div class="row between line"><span>Terms in plan</span><b>{{ terms.length }}</b></div>
        <div class="row between line"><span>Total courses</span><b>{{ terms.flat().length }}</b></div>
        <div class="row between line"><b>Total credits</b><b>{{ totalCredits }}</b></div>
        <div class="actions">
          <button v-if="step > 1" class="btn" @click="step--">Back</button>
          <button v-if="step < 3" class="btn primary" :disabled="!terms.flat().length" @click="next">Next</button>
          <button v-if="step === 3" class="btn primary" :disabled="saving" @click="save"><CalendarCheck :size="16" /> Save Plan</button>
        </div>
        <button v-if="hasDraft" class="btn link small clear-draft" @click="clearDraft">Clear saved draft</button>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { BookOpen, Briefcase, CalendarCheck, ChevronDown, ChevronUp, ClipboardList, Info, LineChart, Plus } from "lucide-vue-next";
import { api } from "../api";
import ProgressBar from "./ProgressBar.vue";
import PlanTerms from "./PlanTerms.vue";
import { PALETTE } from "./palette.js";

const props = defineProps({ student: { type: Object, required: true }, id: { type: String } });
const emit = defineEmits(["changed"]);
const router = useRouter();

const LEVELS = ["degree", "l4_degree", "l5_degree", "gate"];
const LEVEL_LABELS = { degree: "Degree", l4_degree: "L4 Degree", l5_degree: "L5 Degree", gate: "GATE" };
const DRAFT_KEY = "cp_planner_draft";
const max = props.student.max_courses_per_term;
const allTerms = props.student.all_terms || props.student.upcoming_terms;

const courses = ref([]);
const terms = ref([[]]);                 // array of arrays of course ids
const selectedLabels = ref([allTerms[0]]);  // chosen label per term slot
const active = ref(0);
const step = ref(1);
const name = ref("");
const error = ref("");
const saving = ref(false);
const openGroups = ref({});
const hasDraft = ref(false);

// ---------- localStorage persistence ----------
function saveDraft() {
  if (props.id) return;
  const draft = {
    terms: terms.value,
    selectedLabels: selectedLabels.value,
    active: active.value,
    step: step.value,
    name: name.value,
  };
  localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
  hasDraft.value = true;
}

function loadDraft() {
  try {
    const raw = localStorage.getItem(DRAFT_KEY);
    if (!raw) return false;
    const d = JSON.parse(raw);
    if (!Array.isArray(d.terms) || !d.terms.length) return false;
    // Validate labels still exist in allTerms
    const valid = (d.selectedLabels || []).every((l) => allTerms.includes(l));
    if (!valid) return false;
    terms.value = d.terms;
    selectedLabels.value = d.selectedLabels || d.terms.map((_, i) => allTerms[i]);
    active.value = Math.min(d.active ?? 0, d.terms.length - 1);
    step.value = d.step ?? 1;
    name.value = d.name ?? "";
    hasDraft.value = true;
    return true;
  } catch { return false; }
}

function clearDraft() {
  localStorage.removeItem(DRAFT_KEY);
  terms.value = [[]];
  selectedLabels.value = [allTerms[0]];
  active.value = 0;
  step.value = 1;
  name.value = "";
  hasDraft.value = false;
}

// Auto-save on every change
watch([terms, selectedLabels, active, step, name], saveDraft, { deep: true });

onMounted(async () => {
  courses.value = await api.courses();
  if (props.id) {
    try {
      const p = await api.getPlan(props.id);
      name.value = p.name;
      terms.value = p.terms.map(t => t.courses.map(c => c.id));
      selectedLabels.value = p.terms.map(t => t.label);
      active.value = 0;
      step.value = 1;
    } catch (e) {
      error.value = "Failed to load plan for editing: " + e.message;
    }
  } else {
    loadDraft();
  }
});

// ---------- term label helpers ----------
const usedLabels = computed(() => new Set(selectedLabels.value));
const availableTermOptions = computed(() => allTerms);

function onTermSelect(e) {
  const lbl = e.target.value;
  const updated = [...selectedLabels.value];
  updated[active.value] = lbl;
  selectedLabels.value = updated;
}

// ---------- course logic ----------
const byId = computed(() => Object.fromEntries(courses.value.map((c) => [c.id, c])));
const completed = computed(() => new Set(courses.value.filter((c) => c.completed).map((c) => c.id)));

function availableBefore(ts, i) {
  const set = new Set(completed.value);
  for (let k = 0; k < i; k++) ts[k].forEach((id) => set.add(id));
  return set;
}
function normalize(ts) {
  const out = [];
  ts.forEach((t, i) => {
    const avail = availableBefore(out, i);
    out.push(t.filter((id) => byId.value[id]?.prerequisites.every((p) => avail.has(p))));
  });
  return out;
}

function statusOf(c) {
  if (c.completed) return { state: "done", note: "Completed" };
  const inTerm = terms.value.findIndex((t) => t.includes(c.id));
  if (inTerm === active.value) return { state: "selected" };
  if (inTerm >= 0) return { state: "other", note: `Planned in Term ${inTerm + 1}` };
  const avail = availableBefore(terms.value, active.value);
  const missing = c.prerequisites.filter((p) => !avail.has(p));
  if (missing.length) return { state: "locked", note: `Needs: ${missing.join(", ")}` };
  return { state: "ok" };
}

function toggle(c) {
  error.value = "";
  const st = statusOf(c).state;
  if (st === "selected") {
    terms.value = normalize(terms.value.map((t, i) => (i === active.value ? t.filter((x) => x !== c.id) : t)));
  } else if (st === "ok") {
    if (terms.value[active.value].length >= max) { error.value = `Max ${max} courses per term.`; return; }
    terms.value = terms.value.map((t, i) => (i === active.value ? [...t, c.id] : t));
  }
}

function addTerm() {
  if (terms.value.length < allTerms.length) {
    // Find the next unused term label
    const used = new Set(selectedLabels.value);
    const nextLabel = allTerms.find((l) => !used.has(l)) || allTerms[terms.value.length];
    terms.value = [...terms.value, []];
    selectedLabels.value = [...selectedLabels.value, nextLabel];
    active.value = terms.value.length - 1;
  }
}
function removeLastTerm() {
  if (terms.value.length > 1) {
    terms.value = terms.value.slice(0, -1);
    selectedLabels.value = selectedLabels.value.slice(0, -1);
    active.value = Math.min(active.value, terms.value.length - 1);
  }
}

function next() {
  error.value = "";
  const trimmed = [...terms.value];
  const trimmedLabels = [...selectedLabels.value];
  while (trimmed.length && !trimmed[trimmed.length - 1].length) { trimmed.pop(); trimmedLabels.pop(); }
  if (!trimmed.length) { error.value = "Select at least one course."; return; }
  const emptyIdx = trimmed.findIndex((t) => !t.length);
  if (emptyIdx >= 0) { error.value = `Term ${emptyIdx + 1} has no courses. Add some or remove the term.`; return; }
  terms.value = trimmed;
  selectedLabels.value = trimmedLabels;
  active.value = Math.min(active.value, trimmed.length - 1);
  step.value++;
}

async function save() {
  saving.value = true;
  try {
    const planName = name.value.trim() || "My plan";
    if (props.id) {
      await api.updatePlan(props.id, planName, terms.value, selectedLabels.value);
    } else {
      await api.createPlan(planName, terms.value, selectedLabels.value);
    }
    clearDraft();
    emit("changed");
    router.push("/plans");
  } catch (e) { error.value = e.message; saving.value = false; }
}

function itemsFor(lvl) { return courses.value.filter((c) => c.level === lvl); }
function listFor(lvl, kind) { return itemsFor(lvl).filter((c) => c.kind === kind); }
function groupKey(lvl, kind) { return `${lvl}:${kind}`; }
function isOpen(lvl, kind) { const k = groupKey(lvl, kind); return openGroups.value[k] !== false; }
function toggleOpen(lvl, kind) { const k = groupKey(lvl, kind); openGroups.value = { ...openGroups.value, [k]: !isOpen(lvl, kind) }; }

function termCourses(i) { return terms.value[i].map((id) => byId.value[id]).filter(Boolean); }
const activeCourses = computed(() => termCourses(active.value));
const activeCredits = computed(() => activeCourses.value.reduce((n, c) => n + c.credits, 0));
const projects = computed(() => activeCourses.value.filter((c) => c.kind === "project").length);
const totalCredits = computed(() => terms.value.flat().reduce((n, id) => n + (byId.value[id]?.credits ?? 0), 0));
const plannedCredits = computed(() => {
  const selected = new Set(terms.value.flat());
  return courses.value.filter((c) => !c.completed && (c.planned || selected.has(c.id))).reduce((n, c) => n + c.credits, 0);
});
const heading = computed(() => ({
  1: `Select courses you plan to take for ${selectedLabels.value[active.value]}`,
  2: "Review your term-by-term plan",
  3: "Name and save your plan",
}[step.value]));
</script>

<style scoped>
.term-selector-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.5rem 0 0.25rem;
  padding: 0.65rem 1rem;
  background: var(--card, #1e1e2e);
  border-radius: 0.5rem;
  border: 1px solid var(--border, #333);
}
.term-selector-label {
  font-size: 0.9rem;
  color: var(--muted, #aaa);
  white-space: nowrap;
}
.term-select {
  padding: 0.4rem 0.6rem;
  border-radius: 0.4rem;
  border: 1px solid var(--border, #444);
  background: var(--bg, #161622);
  color: var(--fg, #eee);
  font-size: 0.9rem;
  min-width: 180px;
  cursor: pointer;
}
.term-select option:disabled {
  color: #666;
}
.clear-draft {
  margin-top: 0.75rem;
  font-size: 0.8rem;
  opacity: 0.7;
}
.clear-draft:hover {
  opacity: 1;
}
</style>
