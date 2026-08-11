import { apiRequest } from "./client";
import type {
  DataResponse,
  Knowledge,
  KnowledgeCreateRequest,
  KnowledgeFileRole,
  KnowledgeSearchParams,
  KnowledgeUpdateRequest,
} from "./types";

/** Single shared list — search/filter. Default status=ACTIVE narrows to the
 * effective window for non-managers; status=DRAFT requires knowledge:manage. */
export function searchKnowledge(
  params: KnowledgeSearchParams = {},
): Promise<DataResponse<Knowledge[]>> {
  const query = new URLSearchParams();
  if (params.q?.trim()) query.set("q", params.q.trim());
  if (params.type) query.set("type", params.type);
  if (params.status) query.set("status", params.status);
  if (params.referenceOnly) query.set("referenceOnly", "true");
  const qs = query.toString();
  return apiRequest<DataResponse<Knowledge[]>>(
    `/api/v1/knowledge${qs ? `?${qs}` : ""}`,
  );
}

export function fetchKnowledge(id: string): Promise<DataResponse<Knowledge>> {
  return apiRequest<DataResponse<Knowledge>>(
    `/api/v1/knowledge/${encodeURIComponent(id)}`,
  );
}

export function createKnowledge(
  body: KnowledgeCreateRequest,
): Promise<DataResponse<Knowledge>> {
  return apiRequest<DataResponse<Knowledge>>("/api/v1/knowledge", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateKnowledge(
  id: string,
  body: KnowledgeUpdateRequest,
): Promise<DataResponse<Knowledge>> {
  return apiRequest<DataResponse<Knowledge>>(
    `/api/v1/knowledge/${encodeURIComponent(id)}`,
    { method: "PUT", body: JSON.stringify(body) },
  );
}

export function publishKnowledge(id: string): Promise<DataResponse<Knowledge>> {
  return apiRequest<DataResponse<Knowledge>>(
    `/api/v1/knowledge/${encodeURIComponent(id)}/publish`,
    { method: "PUT" },
  );
}

export function archiveKnowledge(id: string): Promise<DataResponse<Knowledge>> {
  return apiRequest<DataResponse<Knowledge>>(
    `/api/v1/knowledge/${encodeURIComponent(id)}/archive`,
    { method: "PUT" },
  );
}

export function deleteKnowledge(id: string): Promise<void> {
  return apiRequest<void>(`/api/v1/knowledge/${encodeURIComponent(id)}`, {
    method: "DELETE",
  });
}

// --- Files (knowledge:manage, DRAFT only) -----------------------------

export function uploadKnowledgeFile(
  knowledgeId: string,
  file: File,
  role: KnowledgeFileRole,
): Promise<DataResponse<Knowledge>> {
  const form = new FormData();
  form.append("file", file);
  form.append("role", role);
  return apiRequest<DataResponse<Knowledge>>(
    `/api/v1/knowledge/${encodeURIComponent(knowledgeId)}/files`,
    { method: "POST", body: form },
  );
}

export function setPrimaryKnowledgeFile(
  knowledgeId: string,
  attachmentId: string,
): Promise<DataResponse<Knowledge>> {
  return apiRequest<DataResponse<Knowledge>>(
    `/api/v1/knowledge/${encodeURIComponent(knowledgeId)}/files/${encodeURIComponent(attachmentId)}/primary`,
    { method: "PUT" },
  );
}

export function removeKnowledgeFile(
  knowledgeId: string,
  attachmentId: string,
): Promise<DataResponse<Knowledge>> {
  return apiRequest<DataResponse<Knowledge>>(
    `/api/v1/knowledge/${encodeURIComponent(knowledgeId)}/files/${encodeURIComponent(attachmentId)}`,
    { method: "DELETE" },
  );
}
