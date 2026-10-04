<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useBandStore } from '../stores/bands'

const auth = useAuthStore()
const bands = useBandStore()

const isAdmin = computed(() => auth.user?.role === 'admin')

const form = reactive({ lightMax: '', heavyMin: '' })
const loadError = ref('')
const error = ref('')
const savedMsg = ref('')
const busy = ref(false)

function syncForm() {
  form.lightMax = bands.lightMax
  form.heavyMin = bands.heavyMin
}

onMounted(async () => {
  loadError.value = ''
  try {
    await bands.load()
    syncForm()
  } catch {
    loadError.value = '分界设置加载失败，请稍后重试'
  }
})

function firstError(data) {
  if (!data) return ''
  if (typeof data === 'string') return data
  if (data.detail) return data.detail
  for (const key of ['non_field_errors', 'lightMax', 'heavyMin']) {
    const v = data[key]
    if (Array.isArray(v) && v.length) return v[0]
  }
  return ''
}

async function submit() {
  error.value = ''
  savedMsg.value = ''
  const light = Number(form.lightMax)
  const heavy = Number(form.heavyMin)
  if (!Number.isInteger(light) || !Number.isInteger(heavy)) {
    error.value = '轻档上限与重档下限都必须是整数克重'
    return
  }
  if (light >= heavy) {
    error.value = '轻档上限必须小于重档下限'
    return
  }
  busy.value = true
  try {
    await bands.save(light, heavy)
    syncForm()
    savedMsg.value = '已保存：晾晒架挂签底色即刻按这套分界上色'
  } catch (e) {
    error.value = firstError(e.response?.data) || '保存失败，请稍后重试'
  } finally {
    busy.value = false
  }
}
</script>

<template>
  <div>
    <header class="rack-head">
      <div>
        <h1>克重色带分界</h1>
        <p class="sub">
          全台唯一一套分界：克重 ≤ 轻档上限染「轻档」色，≥ 重档下限染「重档」色，其间为「中档」。
          保存后晾晒架每条挂签按该卷现行克重上色。
        </p>
      </div>
    </header>

    <p v-if="loadError" class="error">{{ loadError }}</p>

    <template v-if="bands.loaded">
      <section class="panel">
        <div class="band-cards">
          <div class="band-card">
            <span class="hang-tag band-light">轻档</span>
            <span class="range">≤ {{ bands.lightMax }} gsm</span>
            <p class="desc">轻簿帆布，挂签染浅蓝</p>
          </div>
          <div class="band-card">
            <span class="hang-tag band-medium">中档</span>
            <span class="range">{{ bands.mediumRange }} gsm</span>
            <p class="desc">常规克重，挂签染米黄</p>
          </div>
          <div class="band-card">
            <span class="hang-tag band-heavy">重档</span>
            <span class="range">≥ {{ bands.heavyMin }} gsm</span>
            <p class="desc">厚重帆布，挂签染赭红</p>
          </div>
        </div>
        <p class="settings-meta">
          最近保存：{{ bands.updatedAt ? new Date(bands.updatedAt).toLocaleString() : '—' }}
          <template v-if="bands.updatedBy"> · 由 {{ bands.updatedBy }} 写入</template>
        </p>
      </section>

      <section v-if="isAdmin" class="panel">
        <h2 class="feed-title">调整分界（管理员）</h2>
        <p class="hint" style="margin: 0 0 14px">
          只改分界数字，不触碰任何布卷的状态与克重；两名主管交叉提交时，库里只留后写成功的那一版。
        </p>
        <form class="bands-form" @submit.prevent="submit">
          <label>
            轻档上限（gsm，整数）
            <input
              v-model="form.lightMax"
              type="number"
              step="1"
              min="1"
              required
              :disabled="busy"
            />
          </label>
          <label>
            重档下限（gsm，整数）
            <input
              v-model="form.heavyMin"
              type="number"
              step="1"
              min="1"
              required
              :disabled="busy"
            />
          </label>
          <button class="btn" type="submit" :disabled="busy">
            {{ busy ? '保存中…' : '保存分界' }}
          </button>
        </form>
        <p v-if="error" class="error" style="margin: 12px 0 0">{{ error }}</p>
        <p v-if="savedMsg" class="ok" style="margin: 12px 0 0">{{ savedMsg }}</p>
      </section>

      <section v-else class="panel">
        <p class="hint" style="margin: 0">
          当前账号为操作工，仅可查看分界；如需调整请联系管理员。
        </p>
      </section>
    </template>
  </div>
</template>
