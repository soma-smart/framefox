document.addEventListener("DOMContentLoaded", function () {
  // Animation pour les panneaux détaillés
  const profilerItems = document.querySelectorAll(
    "#framefox-profiler .profiler-item"
  );
  const detailsPanel = document.createElement("div");
  detailsPanel.id = "framefox-profiler-details";
  detailsPanel.style.cssText = `
        display: none;
        position: fixed;
        bottom: 36px;
        left: 0;
        right: 0;
        height: 70vh;
        background-color: #fff;
        overflow: auto;
        z-index: 99998;
        box-shadow: 0 -1px 8px rgba(0,0,0,0.2);
        border-top: 1px solid #ddd;
        padding: 20px;
    `;
  document.body.appendChild(detailsPanel);

  let currentPanel = null;

  profilerItems.forEach((item) => {
    item.addEventListener("click", function () {
      const panel = this.getAttribute("data-panel");
      if (!panel) return; // Ignorer si aucun panel n'est spécifié

      const token = document
        .getElementById("framefox-profiler")
        .getAttribute("data-token");

      if (currentPanel === panel && detailsPanel.style.display === "block") {
        detailsPanel.style.display = "none";
        currentPanel = null;
        return;
      }

      currentPanel = panel;
      detailsPanel.style.display = "block";
      detailsPanel.innerHTML = `<div style="text-align:center;padding:20px;">Chargement des détails...</div>`;

      // CORRECTION: Ajouter le préfixe /_profiler/
      fetch(`/_profiler/${token}/${panel}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error(`Erreur HTTP: ${response.status}`);
          }
          return response.text();
        })
        .then((html) => {
          detailsPanel.innerHTML = html;
        })
        .catch((error) => {
          detailsPanel.innerHTML = `
            <div style="padding: 20px; color: red;">
              <h3>Erreur lors du chargement</h3>
              <p>${error.message}</p>
              <p>URL: /_profiler/${token}/${panel}</p>
            </div>
          `;
        });
    });
  });

  // Fermer le panneau quand on clique ailleurs
  document.addEventListener("click", function (event) {
    if (
      detailsPanel.style.display === "block" &&
      !detailsPanel.contains(event.target) &&
      !event.target.closest("#framefox-profiler")
    ) {
      detailsPanel.style.display = "none";
      currentPanel = null;
    }
  });
});
