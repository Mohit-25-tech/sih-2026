import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const uploadDocument = async (file, documentType = 'PASSPORT') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('document_type', documentType);

  const response = await api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getDocumentDetail = async (docId) => {
  const response = await api.get(`/documents/${docId}`);
  return response.data;
};

export const getDocumentsList = async () => {
  const response = await api.get('/documents');
  return response.data;
};

export const getSampleDocuments = async () => {
  const response = await api.get('/documents/samples');
  return response.data;
};

export const loadSampleDocument = async (sampleId) => {
  const response = await api.post(`/documents/load-sample/${sampleId}`);
  return response.data;
};

export const verifyFace = async (documentId, liveImageBase64 = null) => {
  const response = await api.post('/verify-face', {
    document_id: documentId,
    live_image_base64: liveImageBase64,
  });
  return response.data;
};

export const getAuditLogs = async () => {
  const response = await api.get('/audit-logs');
  return response.data;
};

export default api;
