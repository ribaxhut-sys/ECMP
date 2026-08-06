"use client";

import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";
import { useAuth } from "@/auth/AuthProvider";
import { formatIdentityWhen } from "@/features/auth";
import {
  Card,
  CardBody,
  Empty,
  PageContainer,
  PageHeader,
  SectionHeader,
  Skeleton,
} from "@/shared/ui";

export default function ProfileSecurityPage() {
  const router = useRouter();
  const { user, status } = useAuth();
  const t = useTranslations("profile");
  const tCommon = useTranslations("common");
  const lastLogin = formatIdentityWhen(user?.lastLoginAt);

  if (status === "loading") {
    return (
      <PageContainer className="space-y-[var(--ecmp-section-gap)]">
        <Skeleton rows={4} />
      </PageContainer>
    );
  }

  return (
    <PageContainer className="space-y-[var(--ecmp-section-gap)]">
      <PageHeader
        overline={t("overline")}
        title={t("securityTitle")}
        breadcrumbs={[
          { label: tCommon("home"), href: "/dashboard" },
          { label: t("title"), href: "/profile" },
          { label: t("securityTitle") },
        ]}
        description={t("securityPageDescription")}
      />

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("sessionSection")}
          description={t("sessionSectionDescription")}
        />
        <Card>
          <CardBody>
            <Empty
              className="border-0 bg-transparent py-6"
              title={t("sessionUnavailableTitle")}
              description={t("sessionUnavailableDescription")}
              primaryAction={{
                label: t("refreshProfile"),
                onClick: () => router.refresh(),
              }}
            />
          </CardBody>
        </Card>
      </section>

      <section className="space-y-[var(--ecmp-panel-gap)]">
        <SectionHeader
          title={t("lastLoginSection")}
          description={t("lastLoginSectionDescription")}
        />
        <Card>
          <CardBody>
            {lastLogin ? (
              <p className="text-[length:var(--ecmp-font-body-size)] text-ecmp-text-primary">
                <span className="text-ecmp-text-secondary">{t("lastLogin")}: </span>
                {lastLogin}
              </p>
            ) : (
              <Empty
                className="border-0 bg-transparent py-6"
                title={t("lastLoginEmptyTitle")}
                description={t("lastLoginEmptyDescription")}
                primaryAction={{
                  label: t("refreshProfile"),
                  onClick: () => router.refresh(),
                }}
                secondaryAction={{
                  label: tCommon("goToProfile"),
                  onClick: () => router.push("/profile"),
                }}
              />
            )}
          </CardBody>
        </Card>
      </section>
    </PageContainer>
  );
}
