const BACKEND_URL = "http://127.0.0.1:8000";

export async function testZenodoConnection() {
  const response = await fetch(`${BACKEND_URL}/api/zenodo/test`);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail?.error || payload.detail || `Zenodo test failed with status ${response.status}`);
  }
  return payload;
}

export async function uploadDataset(file: File) {
  const formData = new FormData();
  formData.append("file", file);
  
  const response = await fetch(`${BACKEND_URL}/api/incidents/upload`, {
    method: "POST",
    body: formData,
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Upload failed with status ${response.status}`);
  }
  return response.json();
}

export async function analyzeIncident(payload: {
  description: string;
  component?: string;
  severity?: string;
  environment?: string;
  incident_type?: string;
}) {
  const response = await fetch(`${BACKEND_URL}/api/incidents/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Analysis failed with status ${response.status}`);
  }
  return response.json();
}
