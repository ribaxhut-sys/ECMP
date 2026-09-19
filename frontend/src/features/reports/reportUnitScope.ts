import { isPusatUnitCode } from "@/shared/utils";

/**
 * Pusat / Head Office may pick a unit (or all units). Cabang users cannot.
 *
 * Mirrors backend `effective_report_branch_id`: no home branch, or a home
 * unit whose code is Pusat, may scope the report. Anyone else is locked.
 */
export function canPickReportUnit(
  branchId: string | null | undefined,
  homeUnitCode: string | null | undefined,
): boolean {
  if (!branchId?.trim()) return true;
  return isPusatUnitCode(homeUnitCode);
}
