const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

export async function submitProcessRequest(file) {
  const formData = new FormData()

  if (file) {
    formData.append('file', file)
  }

  const response = await fetch(`${API_BASE}/v1/process`, {
    method: 'POST',
    body: formData
  })

  if (!response.ok) {
    throw new Error(`Request failed with status ${response.status}`)
  }

  return response.json()
}
