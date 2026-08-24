(() => {
  const trigger = document.querySelector("#report-request");
  if (!trigger) return;
  trigger.addEventListener("click", (event) => {
    if (!window.Tally || typeof window.Tally.openPopup !== "function") return;
    event.preventDefault();
    const query = new URLSearchParams(window.location.search);
    window.Tally.openPopup(trigger.dataset.formId, {
      layout: "modal",
      width: 500,
      hiddenFields: {
        artifact_id: trigger.dataset.artifactId,
        page_version: trigger.dataset.pageVersion,
        source: query.get("utm_source") || "direct",
      },
    });
  });
})();
