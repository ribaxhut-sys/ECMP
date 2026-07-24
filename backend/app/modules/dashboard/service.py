"""Dashboard orchestration service (TASK-027 / API-319).



Composes responses from KPI, Timeline, and Complaint modules.

Owns no business logic and performs no KPI calculation.

"""



from __future__ import annotations



from app.modules.complaints.service import ComplaintService

from app.modules.dashboard.schemas import (

    DashboardHeader,

    DashboardRecentActivityItem,

    DashboardSlaStage,

    DashboardSlaSummary,

    DashboardSummaryResponse,

)

from app.modules.kpi.service import KpiService

from app.modules.settings.registry import SettingsKey

from app.modules.settings.service import SettingsService

from app.modules.timelines.service import TimelineService



_DEFAULT_RECENT_LIMIT = 10

_SYSTEM_ACTOR = "SYSTEM"





class DashboardService:

    def __init__(

        self,

        *,

        kpi_service: KpiService,

        timeline_service: TimelineService,

        complaint_service: ComplaintService,

        settings_service: SettingsService,

    ) -> None:

        self._kpi = kpi_service

        self._timeline = timeline_service

        self._complaints = complaint_service

        self._settings = settings_service



    def summary(self) -> DashboardSummaryResponse:

        """Compose header + SLA + recent activity from existing modules."""

        kpi = self._kpi.summary()

        recent_limit = self._settings.get_int(

            SettingsKey.DASHBOARD_RECENT_LIMIT,

            default=_DEFAULT_RECENT_LIMIT,

        )

        if recent_limit < 1:

            recent_limit = _DEFAULT_RECENT_LIMIT

        rows = self._timeline.list_recent(limit=recent_limit)



        recent: list[DashboardRecentActivityItem] = []

        for row in rows:

            complaint = self._complaints.get(row.complaint_id)

            actor = row.__dict__.get("actor")

            actor_name = getattr(actor, "full_name", None) if actor is not None else None

            if not actor_name:

                meta = row.metadata_json if isinstance(row.metadata_json, dict) else None

                meta_actor = meta.get("actor") if meta else None

                actor_name = str(meta_actor) if meta_actor else _SYSTEM_ACTOR



            recent.append(

                DashboardRecentActivityItem(

                    eventType=str(row.event_type),

                    complaintNumber=complaint.complaint_number,

                    timestamp=row.event_at,

                    actor=actor_name,

                )

            )



        return DashboardSummaryResponse(

            header=DashboardHeader(

                totalComplaints=kpi.complaints.total,

                openComplaints=kpi.complaints.open,

                closedComplaints=kpi.complaints.closed,

            ),

            sla=DashboardSlaSummary(

                assignment=DashboardSlaStage(

                    completed=kpi.assignment.completed,

                    breached=kpi.assignment.breached,

                ),

                appointment=DashboardSlaStage(

                    completed=kpi.appointment.completed,

                    breached=kpi.appointment.breached,

                ),

                resolution=DashboardSlaStage(

                    completed=kpi.resolution.completed,

                    breached=kpi.resolution.breached,

                ),

                escalation=DashboardSlaStage(

                    completed=kpi.escalation.completed,

                    breached=kpi.escalation.breached,

                ),

                overall=DashboardSlaStage(

                    completed=kpi.overall.completed,

                    breached=kpi.overall.breached,

                ),

            ),

            recentActivity=recent,

        )

