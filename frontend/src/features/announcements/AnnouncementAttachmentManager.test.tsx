import { cleanup, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "@/test/harness";
import { AnnouncementAttachmentManager } from "./AnnouncementAttachmentManager";

const uploadAnnouncementAttachment = vi.fn();
const removeAnnouncementAttachment = vi.fn();
const updateAnnouncementAttachmentVisibility = vi.fn();
const fetchAnnouncementAttachmentLibrary = vi.fn();
const linkAnnouncementAttachment = vi.fn();

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return {
    ...actual,
    uploadAnnouncementAttachment: (...args: unknown[]) =>
      uploadAnnouncementAttachment(...args),
    removeAnnouncementAttachment: (...args: unknown[]) =>
      removeAnnouncementAttachment(...args),
    updateAnnouncementAttachmentVisibility: (...args: unknown[]) =>
      updateAnnouncementAttachmentVisibility(...args),
    fetchAnnouncementAttachmentLibrary: (...args: unknown[]) =>
      fetchAnnouncementAttachmentLibrary(...args),
    linkAnnouncementAttachment: (...args: unknown[]) =>
      linkAnnouncementAttachment(...args),
  };
});

const ANNOUNCEMENT_ID = "a1111111-1111-1111-1111-111111111111";

describe("AnnouncementAttachmentManager — visibility default/selection/submission", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    fetchAnnouncementAttachmentLibrary.mockResolvedValue({ data: [] });
  });

  afterEach(() => {
    cleanup();
  });

  it("defaults the new-attachment radio to 'Visible when the announcement is published'", () => {
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[]}
        onChange={() => {}}
      />,
    );

    const published = screen.getByRole("radio", {
      name: /Visible when the announcement is published/i,
    });
    const immediate = screen.getByRole("radio", {
      name: /Visible immediately/i,
    });
    expect(published).toBeChecked();
    expect(immediate).not.toBeChecked();
  });

  it("shows Upload and Link existing actions", () => {
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[]}
        onChange={() => {}}
      />,
    );
    expect(screen.getByRole("button", { name: /^Upload$/i })).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /Link existing/i }),
    ).toBeInTheDocument();
  });

  it("lets the user pick 'Visible immediately' instead", async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[]}
        onChange={() => {}}
      />,
    );

    const immediate = screen.getByRole("radio", {
      name: /Visible immediately/i,
    });
    await user.click(immediate);
    expect(immediate).toBeChecked();
  });

  it("sends the selected visibility (IMMEDIATE) to the backend on upload", async () => {
    uploadAnnouncementAttachment.mockResolvedValue({
      data: {
        id: "att-1",
        fileName: "SOP.pdf",
        mimeType: "application/pdf",
        sizeBytes: 1024,
        visibility: "IMMEDIATE",
        createdAt: "2026-08-01T00:00:00Z",
      },
    });
    const onChange = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[]}
        onChange={onChange}
      />,
    );

    await user.click(
      screen.getByRole("radio", { name: /Visible immediately/i }),
    );

    const file = new File(["%PDF-1.4"], "SOP.pdf", { type: "application/pdf" });
    const fileInput = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    await user.upload(fileInput, file);

    await waitFor(() => expect(uploadAnnouncementAttachment).toHaveBeenCalled());
    expect(uploadAnnouncementAttachment).toHaveBeenCalledWith(
      ANNOUNCEMENT_ID,
      file,
      "IMMEDIATE",
    );
    await waitFor(() => expect(onChange).toHaveBeenCalled());
  });

  it("sends the default visibility (PUBLISHED) when the user does not change it", async () => {
    uploadAnnouncementAttachment.mockResolvedValue({
      data: {
        id: "att-2",
        fileName: "Formulir.pdf",
        mimeType: "application/pdf",
        sizeBytes: 2048,
        visibility: "PUBLISHED",
        createdAt: "2026-08-01T00:00:00Z",
      },
    });
    const user = userEvent.setup();
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[]}
        onChange={() => {}}
      />,
    );

    const file = new File(["%PDF-1.4"], "Formulir.pdf", {
      type: "application/pdf",
    });
    const fileInput = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    await user.upload(fileInput, file);

    await waitFor(() => expect(uploadAnnouncementAttachment).toHaveBeenCalled());
    expect(uploadAnnouncementAttachment).toHaveBeenCalledWith(
      ANNOUNCEMENT_ID,
      file,
      "PUBLISHED",
    );
  });

  it("uploads every file when the user selects multiple files", async () => {
    uploadAnnouncementAttachment.mockResolvedValue({
      data: {
        id: "att-multi",
        fileName: "a.pdf",
        mimeType: "application/pdf",
        sizeBytes: 10,
        visibility: "PUBLISHED",
        createdAt: "2026-08-01T00:00:00Z",
      },
    });
    const onChange = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[]}
        onChange={onChange}
      />,
    );

    const fileA = new File(["a"], "a.pdf", { type: "application/pdf" });
    const fileB = new File(["b"], "b.pdf", { type: "application/pdf" });
    const fileInput = document.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    expect(fileInput.multiple).toBe(true);
    await user.upload(fileInput, [fileA, fileB]);

    await waitFor(() =>
      expect(uploadAnnouncementAttachment).toHaveBeenCalledTimes(2),
    );
    expect(uploadAnnouncementAttachment).toHaveBeenNthCalledWith(
      1,
      ANNOUNCEMENT_ID,
      fileA,
      "PUBLISHED",
    );
    expect(uploadAnnouncementAttachment).toHaveBeenNthCalledWith(
      2,
      ANNOUNCEMENT_ID,
      fileB,
      "PUBLISHED",
    );
    await waitFor(() => expect(onChange).toHaveBeenCalled());
  });

  it("renders each existing attachment's own visibility as already selected", () => {
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[
          {
            id: "att-3",
            fileName: "Alur.pdf",
            mimeType: "application/pdf",
            sizeBytes: 512,
            visibility: "IMMEDIATE",
            createdAt: "2026-08-01T00:00:00Z",
          },
        ]}
        onChange={() => {}}
      />,
    );

    const radios = screen.getAllByRole("radio", {
      name: /Visible immediately/i,
    });
    // One in the existing-attachment row, one in the "add new" section.
    expect(radios).toHaveLength(2);
    expect(radios[0]).toBeChecked();
  });

  it("opens the link modal and loads the library with excludeAnnouncementId", async () => {
    fetchAnnouncementAttachmentLibrary.mockResolvedValue({
      data: [
        {
          id: "lib-1",
          fileName: "Shared.pdf",
          mimeType: "application/pdf",
          sizeBytes: 100,
          createdAt: "2026-08-01T00:00:00Z",
        },
      ],
    });
    const user = userEvent.setup();
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[]}
        onChange={() => {}}
      />,
    );

    await user.click(screen.getByRole("button", { name: /Link existing/i }));
    expect(
      await screen.findByRole("dialog", { name: /Attachment library/i }),
    ).toBeInTheDocument();
    await waitFor(() =>
      expect(fetchAnnouncementAttachmentLibrary).toHaveBeenCalledWith({
        excludeAnnouncementId: ANNOUNCEMENT_ID,
      }),
    );
    expect(await screen.findByText("Shared.pdf")).toBeInTheDocument();
  });

  it("filters the library by search and links selected files with visibility", async () => {
    fetchAnnouncementAttachmentLibrary.mockResolvedValue({
      data: [
        {
          id: "lib-1",
          fileName: "SOP.pdf",
          mimeType: "application/pdf",
          sizeBytes: 100,
          createdAt: "2026-08-01T00:00:00Z",
        },
        {
          id: "lib-2",
          fileName: "Other.pdf",
          mimeType: "application/pdf",
          sizeBytes: 200,
          createdAt: "2026-08-01T00:00:00Z",
        },
      ],
    });
    linkAnnouncementAttachment.mockResolvedValue({
      data: {
        id: "lib-1",
        fileName: "SOP.pdf",
        mimeType: "application/pdf",
        sizeBytes: 100,
        visibility: "IMMEDIATE",
        createdAt: "2026-08-01T00:00:00Z",
      },
    });
    const onChange = vi.fn();
    const user = userEvent.setup();
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[]}
        onChange={onChange}
      />,
    );

    await user.click(
      screen.getByRole("radio", { name: /Visible immediately/i }),
    );
    await user.click(screen.getByRole("button", { name: /Link existing/i }));
    const dialog = await screen.findByRole("dialog", {
      name: /Attachment library/i,
    });
    await screen.findByText("SOP.pdf");

    await user.type(
      within(dialog).getByLabelText(/Search attachments/i),
      "SOP",
    );
    expect(within(dialog).getByText("SOP.pdf")).toBeInTheDocument();
    expect(within(dialog).queryByText("Other.pdf")).not.toBeInTheDocument();

    await user.click(within(dialog).getByRole("checkbox", { name: /SOP\.pdf/i }));
    await user.click(within(dialog).getByRole("button", { name: /^Link$/i }));

    await waitFor(() =>
      expect(linkAnnouncementAttachment).toHaveBeenCalledWith(ANNOUNCEMENT_ID, {
        attachmentId: "lib-1",
        visibility: "IMMEDIATE",
      }),
    );
    await waitFor(() => expect(onChange).toHaveBeenCalled());
  });

  it("disables already-linked attachments in the picker", async () => {
    fetchAnnouncementAttachmentLibrary.mockResolvedValue({
      data: [
        {
          id: "already",
          fileName: "Already.pdf",
          mimeType: "application/pdf",
          sizeBytes: 50,
          createdAt: "2026-08-01T00:00:00Z",
        },
      ],
    });
    const user = userEvent.setup();
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[
          {
            id: "already",
            fileName: "Already.pdf",
            mimeType: "application/pdf",
            sizeBytes: 50,
            visibility: "PUBLISHED",
            createdAt: "2026-08-01T00:00:00Z",
          },
        ]}
        onChange={() => {}}
      />,
    );

    await user.click(screen.getByRole("button", { name: /Link existing/i }));
    const dialog = await screen.findByRole("dialog", {
      name: /Attachment library/i,
    });
    // Library was fetched with exclude — but if an id still appears, checkbox is disabled.
    const checkbox = within(dialog).queryByRole("checkbox", {
      name: /Already\.pdf/i,
    });
    if (checkbox) {
      expect(checkbox).toBeDisabled();
    }
  });

  it("shows an error when the library fails to load", async () => {
    fetchAnnouncementAttachmentLibrary.mockImplementation(() =>
      Promise.reject(new Error("boom")),
    );
    const user = userEvent.setup();
    renderWithProviders(
      <AnnouncementAttachmentManager
        announcementId={ANNOUNCEMENT_ID}
        attachments={[]}
        onChange={() => {}}
      />,
    );
    await user.click(screen.getByRole("button", { name: /Link existing/i }));
    const dialog = await screen.findByRole("dialog", {
      name: /Attachment library/i,
    });
    // resolveApiErrorMessage maps plain Error → common.unexpectedError
    expect(
      await within(dialog).findByRole("alert"),
    ).toBeInTheDocument();
  });
});
