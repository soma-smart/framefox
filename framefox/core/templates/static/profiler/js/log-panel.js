(function () {
  // Fonction pour initialiser le panel de logs
  function initLogPanel() {
    // Trouver le panel dans le parent le plus proche
    const panel = document.querySelector("#panel-content .log-panel");
    if (!panel) return;

    // Éléments DOM
    const filterInput = panel.querySelector(".log-filter");
    const clearFilterBtn = panel.querySelector(".clear-filter");
    const levelFilter = panel.querySelector(".log-level-filter");
    const limitSelect = panel.querySelector(".log-limit");
    const logsContainer = panel.querySelector(".logs-container");
    const loadMoreContainer = panel.querySelector(".load-more-container");
    const loadMoreBtn = panel.querySelector(".load-more-btn");
    const showingCount = panel.querySelector(".showing-count");

    // Vérifier que tous les éléments sont présents
    if (
      !filterInput ||
      !clearFilterBtn ||
      !levelFilter ||
      !limitSelect ||
      !logsContainer ||
      !loadMoreContainer ||
      !loadMoreBtn ||
      !showingCount
    ) {
      return;
    }

    // Configuration
    // Inverser l'ordre pour afficher les plus récents d'abord (les records arrivent avec les plus anciens en premier)
    const allLogEntries = Array.from(
      logsContainer.querySelectorAll(".log-entry")
    ).reverse();

    // Remplacer les entrées existantes dans le DOM par les entrées inversées
    logsContainer.innerHTML = "";
    allLogEntries.forEach((entry) => {
      logsContainer.appendChild(entry);
    });

    let filteredEntries = [...allLogEntries];
    let visibleLimit = parseInt(limitSelect.value) || 50;
    let activeDebounce = null;

    // Fonction pour mettre à jour la visibilité des entrées
    function updateVisibility() {
      const entriesToShow = filteredEntries.slice(0, visibleLimit);
      const entrySet = new Set(entriesToShow);

      // Mettre à jour la visibilité sans recréer les éléments
      allLogEntries.forEach((entry) => {
        entry.style.display = entrySet.has(entry) ? "" : "none";
      });

      // Afficher/masquer "Load more"
      loadMoreContainer.style.display =
        filteredEntries.length > visibleLimit ? "block" : "none";

      // Mettre à jour le compteur
      const visibleCount = Math.min(visibleLimit, filteredEntries.length);
      showingCount.textContent = `Showing ${visibleCount} of ${filteredEntries.length} entries`;
    }

    // Fonction de filtrage avec debounce
    function filterLogs() {
      // Effacer tout debounce précédent
      if (activeDebounce) {
        clearTimeout(activeDebounce);
      }

      // Configurer un nouveau debounce
      activeDebounce = setTimeout(() => {
        const filterText = filterInput.value.toLowerCase();
        const levelValue = levelFilter.value;

        // Bouton de nettoyage du filtre
        clearFilterBtn.style.display = filterText ? "block" : "none";

        // Filtrer les entrées
        filteredEntries = allLogEntries.filter((entry) => {
          const message = entry
            .querySelector(".message-col")
            .textContent.toLowerCase();
          const level = entry.getAttribute("data-level").toLowerCase();

          const matchesText = !filterText || message.includes(filterText);
          const matchesLevel = levelValue === "all" || level === levelValue;

          return matchesText && matchesLevel;
        });

        // Ajuster la limite de visibilité
        if (limitSelect.value === "all") {
          visibleLimit = filteredEntries.length;
        } else {
          visibleLimit = parseInt(limitSelect.value) || 50;
        }

        updateVisibility();
      }, 100);
    }

    // Listeners d'événements
    filterInput.addEventListener("input", filterLogs);
    levelFilter.addEventListener("change", filterLogs);
    limitSelect.addEventListener("change", function () {
      visibleLimit =
        this.value === "all" ? filteredEntries.length : parseInt(this.value);
      updateVisibility();
    });
    clearFilterBtn.addEventListener("click", function () {
      filterInput.value = "";
      filterLogs();
    });
    loadMoreBtn.addEventListener("click", function () {
      visibleLimit += 50;
      updateVisibility();
    });

    // Initialisation - appliquer immédiatement la limite sélectionnée
    updateVisibility();
  }

  // Enregistrer pour l'événement personnalisé
  document.addEventListener("panel-loaded", function (e) {
    if (e.detail && e.detail.panelName === "log") {
      setTimeout(initLogPanel, 50);
    }
  });
})();
