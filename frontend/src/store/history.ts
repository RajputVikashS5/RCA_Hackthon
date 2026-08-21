import { create } from 'zustand'
import { deleteAnalysis, getAnalysisHistory, type AnalysisResult, type IncidentInput, type StoredAnalysis as ApiStoredAnalysis } from '../api'

export type StoredAnalysis = { id: string; createdAt: string; input: IncidentInput; result: AnalysisResult }
type HistoryStore = { items: StoredAnalysis[]; add: (input: IncidentInput, result: AnalysisResult) => StoredAnalysis; remove: (id: string) => void; refresh: () => Promise<void> }
const normalize = (item: ApiStoredAnalysis): StoredAnalysis => ({ id: item.id, createdAt: item.created_at, input: item.input, result: item.result })
export const useHistoryStore = create<HistoryStore>((set, get) => ({
  items: [],
  add: (input, result) => { const item = { id: result.analysis_id || crypto.randomUUID(), createdAt: new Date().toISOString(), input, result }; set({ items: [item, ...get().items.filter((old) => old.id !== item.id)] }); return item },
  remove: (id) => { set({ items: get().items.filter((item) => item.id !== id) }); void deleteAnalysis(id).catch(() => get().refresh()) },
  refresh: async () => { const items = await getAnalysisHistory(); set({ items: items.map(normalize) }) },
}))
void useHistoryStore.getState().refresh().catch(() => undefined)
