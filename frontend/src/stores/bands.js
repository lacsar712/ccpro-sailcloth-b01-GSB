import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import api from '../api'

// 克重色带分界：唯一事实来源是后端单行设置（/api/gsm-bands/）。
// 每次加载都从服务端取，保证刷新/换间再回来后挂签底色仍跟随库里那一版。
export const useBandStore = defineStore('bands', () => {
  const lightMax = ref(null)
  const heavyMin = ref(null)
  const updatedAt = ref(null)
  const updatedBy = ref(null)
  const loaded = ref(false)

  function apply(data) {
    lightMax.value = data.lightMax
    heavyMin.value = data.heavyMin
    updatedAt.value = data.updatedAt || null
    updatedBy.value = data.updatedBy || null
    loaded.value = true
  }

  async function load() {
    const { data } = await api.get('/gsm-bands/')
    apply(data)
  }

  async function save(light, heavy) {
    const { data } = await api.put('/gsm-bands/', {
      lightMax: light,
      heavyMin: heavy,
    })
    apply(data)
    return data
  }

  // 与后端 GsmBandSettings.band_for 同一套规则：
  // gsm <= lightMax → 轻；gsm >= heavyMin → 重；其余 → 中
  function bandOf(gsm) {
    if (!loaded.value) return 'medium'
    const g = Number(gsm)
    if (g <= lightMax.value) return 'light'
    if (g >= heavyMin.value) return 'heavy'
    return 'medium'
  }

  const mediumRange = computed(() => {
    if (!loaded.value) return ''
    return `${lightMax.value + 1}–${heavyMin.value - 1}`
  })

  return {
    lightMax,
    heavyMin,
    updatedAt,
    updatedBy,
    loaded,
    load,
    save,
    bandOf,
    mediumRange,
  }
})
