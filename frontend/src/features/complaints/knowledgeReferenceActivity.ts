import type { Knowledge, KnowledgeStatus, KnowledgeType } from "@/lib/api/types";

/** ACTIVE + within effective window — same idea as backend `within_effective_window`. */
export function isKnowledgeReferenceActive(
  knowledge: Pick<Knowledge, "status" | "effectiveFrom" | "effectiveTo">,
  now: Date = new Date(),
): boolean {
  if (knowledge.status !== "ACTIVE") return false;
  if (knowledge.effectiveFrom) {
    const from = new Date(knowledge.effectiveFrom);
    if (!Number.isNaN(from.getTime()) && from > now) return false;
  }
  if (knowledge.effectiveTo) {
    const to = new Date(knowledge.effectiveTo);
    if (!Number.isNaN(to.getTime()) && to < now) return false;
  }
  return true;
}

export type KnowledgeReferenceMeta = {
  active: boolean;
  knowledgeType?: KnowledgeType;
  status?: KnowledgeStatus;
};
