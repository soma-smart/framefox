// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
  // Les assets et liens Starlight seront préfixés avec /docs
  base: "/",
  integrations: [
    starlight({
      title: "Framefox Documentation",
      description:
        "Framework web Python moderne pour développer rapidement des applications robustes",
      //   logo: {
      //     // src: "./src/assets/framefox-logo.svg",
      //     // replacesTitle: true,
      //   },
      social: [
        {
          icon: "github",
          label: "GitHub",
          href: "https://github.com/soma-smart/framefox",
        },
      ],
      editLink: {
        baseUrl: "https://github.com/soma-smart/framefox/edit/main/docs/",
      },
      lastUpdated: true,
      sidebar: [
        {
          label: "Démarrage",
          items: [
            { label: "Guide de démarrage rapide", slug: "index" },
            { label: "Installation", slug: "docs/installation" },
          ],
        },
        {
          label: "docs principaux",
          items: [
            { label: "Contrôleurs", slug: "docs/controllers" },
            { label: "Système de routing", slug: "docs/routing" },
            { label: "Templates et vues", slug: "docs/templates" },
            { label: "Base de données et ORM", slug: "docs/database" },
            { label: "Formulaires et validation", slug: "docs/forms" },
            { label: "Authentification et sécurité", slug: "docs/security" },
          ],
        },
        {
          label: "Fonctionnalités avancées",
          items: [
            { label: "Middleware et événements", slug: "docs/middleware" },
            {
              label: "Services et injection de dépendances",
              slug: "docs/services",
            },
            { label: "Terminal et commandes", slug: "docs/terminal" },
            { label: "Tests", slug: "docs/testing" },
            { label: "Déploiement", slug: "docs/deployment" },
          ],
        },
        {
          label: "Référence API",
          autogenerate: { directory: "reference" },
        },
        {
          label: "Exemples",
          items: [
            // { label: "Application de blog", slug: "examples/blog" },
            // { label: "API REST", slug: "examples/api" },
            // { label: "Authentification complète", slug: "examples/auth" },
          ],
        },
      ],
      customCss: ["./src/styles/custom.css"],
    }),
  ],
});
