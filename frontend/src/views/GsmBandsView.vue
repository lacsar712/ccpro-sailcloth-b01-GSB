<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const isAdmin = computed(() => auth.user?.role === 'admin')

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const saved = ref('')
const meta = ref({ updatedBy: '', updatedAt: '' })

const form = reactive({
  lightMax: null,
  heavyMin: null,
})

const bandLabel = { light: '轻档', medium: '中档', heavy: '重档' }

const preview = computed(() => {
  const light = Number(form.lightMax)
  const heavy = Number(form.heavyMin)
  const valid =
    Number.isInteger(light) && Number.isInteger(heavy) && light >= 1 && light < heavy
  return { light, heavy, valid }
})

async function load() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.get('/gsm-bands/')
    form.lightMax = data.lightMax
    form.heavyMin = data.heavyMin
    meta.value = { updatedBy: data.updatedBy, updatedAt: data.updatedAt }
  } catch {
    error.value = '分界加载失败'
  } finally {
    loading.value = false
  }
}

async function save() {
  if (!isAdmin.value || saving.value) return
  error.value = ''
  saved.value = ''
  saving.value = true
  try {
    const { data } = await api.put('/gsm-bands/', {
      lightMax: form.lightMax,
      heavyMin: form.heavyMin,
    })
    form.lightMax = data.lightMax
    form.heavyMin = data.heavyMin
    meta.value = { updatedBy: data.updatedBy, updatedAt: data.updatedAt }
    saved.value = '已保存，晾晒架挂签底色即刻按新分界执行'
  } catch (e) {
    const data = e.response?.data
    error.value =
      data?.heavyMin?.[0] ||
      data?.lightMax?.[0] ||
      data?.detail ||
      '保存失败（轻档上限须小于重档下限，且均为整数克重）'
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>

<template>
  <div>
    <h1>克重色带分界</h1>
    <p class="sub">
      按布卷现行克重落入轻 / 中 / 重档决定晾晒架挂签底色。全台仅此一版分界，后写覆盖先写。
    </p>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="saved" class="ok">{{ saved }}</p>

    <form class="panel row" @submit.prevent="save">
      <label>轻档上限 gsm（≤ 此值入轻档）
        <input
          v-model.number="form.lightMax"
          type="number"
          step="1"
          min="1"
          :disabled="!isAdmin || loading"
          required
        />
      </label>
      <label>重档下限 gsm（≥ 此值入重档）
        <input
          v-model.number="form.heavyMin"
          type="number"
          step="1"
          min="1"
          :disabled="!isAdmin || loading"
          required
        />
      </label>
      <button v-if="isAdmin" class="btn" type="submit" :disabled="saving || loading || !preview.valid">
        {{ saving ? '保存中…' : '保存分界' }}
      </button>
      <p v-else class="hint" style="align-self: center">操作工仅可查看，分界由管理员维护。</p>
    </form>

    <p v-if="form.lightMax !== null && !preview.valid" class="error">
      轻档上限必须小于重档下限，且均为正整数克重。
    </p>

    <section class="panel">
      <h2 class="feed-title">色带预览</h2>
      <p class="hint" style="margin: 0 0 12px">
        <template v-if="preview.valid">
          轻档 ≤ {{ preview.light }} gsm · 中档 {{ preview.light + 1 }}–{{ preview.heavy - 1 }} gsm · 重档 ≥ {{ preview.heavy }} gsm
        </template>
        <template v-else>分界无效时暂不预览。</template>
      </p>
      <div class="band-preview">
        <span v-for="band in ['light', 'medium', 'heavy']" :key="band" class="hang-tag" :class="'band-' + band">
          {{ bandLabel[band] }}
        </span>
      </div>
      <p v-if="meta.updatedAt" class="hint" style="margin: 12px 0 0">
        最近由 {{ meta.updatedBy || '—' }} 更新于 {{ new Date(meta.updatedAt).toLocaleString() }}
      </p>
    </section>
  </div>
</template>
