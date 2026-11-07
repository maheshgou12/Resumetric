import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import api from '../lib/api'

export default function ResumesPage() {
  const qc = useQueryClient()
  const [name, setName] = useState('')
  const [targetRole, setTargetRole] = useState('')
  const [file, setFile] = useState(null)
  const [compareIds, setCompareIds] = useState([])
  const [compareResult, setCompareResult] = useState(null)

  const { data: resumes = [], isLoading } = useQuery({
    queryKey: ['resumes'],
    queryFn: () => api.get('/career/resumes').then(r => r.data),
  })

  const upload = useMutation({
    mutationFn: (fd) => api.post('/career/resumes', fd, { headers: { 'Content-Type': 'multipart/form-data' } }),
    onSuccess: (r) => {
      toast.success(`Uploaded v${r.data.version} — Score ${r.data.resume_score.overall}/100`)
      qc.invalidateQueries(['resumes'])
      setFile(null); setName('')
    },
    onError: (e) => toast.error(e.response?.data?.detail || 'Upload failed'),
  })

  const del = useMutation({
    mutationFn: (id) => api.delete(`/career/resumes/${id}`),
    onSuccess: () => { toast.success('Deleted'); qc.invalidateQueries(['resumes']) },
    onError: () => toast.error('Delete failed'),
  })

  const reanalyze = useMutation({
    mutationFn: (id) => api.post(`/career/resumes/${id}/reanalyze`),
    onSuccess: (r) => { toast.success(`Re-scored: ${r.data.resume_score.overall}/100`); qc.invalidateQueries(['resumes']) },
    onError: () => toast.error('Re-analyze failed'),
  })

  const download = async (r) => {
    let url = null
    try {
      const resp = await api.get(`/career/resumes/${r.id}/download`, { responseType: 'blob' })
      const mime = resp.headers?.['content-type'] || 'text/plain;charset=utf-8'
      const blob = resp.data instanceof Blob ? resp.data : new Blob([resp.data], { type: mime })
      url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${(r.name || 'resume').replace(/[^\w\-]+/g, '-')}-v${r.version}.txt`
      document.body.appendChild(a)
      a.click()
      a.remove()
    } catch { toast.error('Download failed') }
    finally { if (url) setTimeout(() => URL.revokeObjectURL(url), 5000) }
  }

  const toggleCompare = (id) => {
    setCompareIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id].slice(-2))
  }

  const runCompare = async () => {
    if (compareIds.length !== 2) return toast.error('Select exactly 2 resumes to compare')
    try {
      const r = await api.post('/career/resumes/compare', { resume_a_id: compareIds[0], resume_b_id: compareIds[1] })
      setCompareResult(r.data)
    } catch { toast.error('Compare failed') }
  }

  return (
    <div style={{ maxWidth: 1000, margin: '0 auto', padding: '2.5rem 1.5rem', flex: 1 }}>
      <h1 style={{ fontSize: '1.875rem', marginBottom: '.25rem' }}>Resume Library</h1>
      <p style={{ color: '#64748b', marginBottom: '1.5rem' }}>Upload multiple resumes, track versions, re-analyze, compare, download.</p>

      <div className="card">
        <h3>Upload new resume (PDF / DOCX, max 5MB)</h3>
        <div style={{ display: 'flex', gap: '.75rem', flexWrap: 'wrap', marginTop: '.75rem' }}>
          <input className="input" placeholder="Resume label e.g. Backend-v2" value={name} onChange={e => setName(e.target.value)} style={{ flex: 1, minWidth: 180 }} />
          <input className="input" placeholder="Target role e.g. Backend Developer" value={targetRole} onChange={e => setTargetRole(e.target.value)} style={{ flex: 1, minWidth: 180 }} />
          <input type="file" accept=".pdf,.docx,.doc" onChange={e => setFile(e.target.files[0])} />
          <button className="btn-primary" disabled={!file || upload.isPending} onClick={() => {
            const fd = new FormData()
            fd.append('resume', file); fd.append('name', name); fd.append('target_role', targetRole)
            upload.mutate(fd)
          }}>{upload.isPending ? 'Uploading...' : 'Upload + Score'}</button>
        </div>
      </div>

      <div className="card" style={{ marginTop: '1rem' }}>
        <h3>Your resumes ({resumes.length}) — tick 2 to compare versions</h3>
        {isLoading ? <p>Loading...</p> : resumes.length === 0 ? <p style={{ color: '#64748b' }}>No resumes yet. Upload your first one above.</p> : (
          <table style={{ width: '100%', fontSize: '.875rem', marginTop: '.5rem' }}>
            <thead><tr style={{ color: '#64748b', textAlign: 'left' }}>
              <th></th><th>Name</th><th>Ver</th><th>Role</th><th>Score</th><th>Words</th><th>Actions</th>
            </tr></thead>
            <tbody>
              {resumes.map(r => (
                <tr key={r.id} style={{ borderTop: '1px solid rgba(255,255,255,.06)' }}>
                  <td><input type="checkbox" checked={compareIds.includes(r.id)} onChange={() => toggleCompare(r.id)} /></td>
                  <td>{r.name}</td>
                  <td>v{r.version}</td>
                  <td>{r.target_role || '—'}</td>
                  <td><b style={{ color: (r.resume_score?.overall ?? 0) >= 70 ? '#34d399' : '#fbbf24' }}>{r.resume_score?.overall ?? '—'}/100</b></td>
                  <td>{r.words}</td>
                  <td style={{ display: 'flex', gap: '.4rem', flexWrap: 'wrap' }}>
                    <button className="btn-ghost" onClick={() => reanalyze.mutate(r.id)}>Re-analyze</button>
                    <button className="btn-ghost" onClick={() => download(r)}>Download</button>
                    <button className="btn-ghost" style={{ color: '#f87171' }} onClick={() => del.mutate(r.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
        {resumes.length >= 2 && (
          <div style={{ marginTop: '.75rem' }}>
            <button className="btn-primary" onClick={runCompare}>Compare selected (2)</button>
          </div>
        )}
      </div>

      {compareResult && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <h3>{compareResult.verdict}</h3>
          <p style={{ fontSize: '.875rem' }}>Similarity {compareResult.text_diff.similarity_pct}% | +{compareResult.text_diff.words_added} words</p>
          <p style={{ color: '#34d399', fontSize: '.875rem' }}>Added skills: {compareResult.skills_added.join(', ') || '—'}</p>
          <p style={{ color: '#f87171', fontSize: '.875rem' }}>Removed: {compareResult.skills_removed.join(', ') || '—'}</p>
          <p style={{ fontSize: '.875rem' }}>Delta: {compareResult.score_delta > 0 ? '+' : ''}{compareResult.score_delta} pts</p>
        </div>
      )}
    </div>
  )
}
