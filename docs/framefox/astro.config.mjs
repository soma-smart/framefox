// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
  site: "https://soma-smart.github.io",
  base: "/framefox/",
  integrations: [
    starlight({
      title: "Framefox",
      description:
        "Modern Python web framework for rapidly developing robust applications",
      logo: {
        src: "./public/orangefox.png",
        // replacesTitle: true,
      },
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
          label: "Getting Started",
          items: [
            { label: "Introduction", slug: "introduction" },
            { label: "Quick Start Guide", slug: "quick_start" },
            { label: "Installation", slug: "installation" },
          ],
        },
        {
          label: "Core Documentation",
          items: [
            { label: "Controllers", slug: "core/controllers" },
            { label: "Routing System", slug: "core/routing" },
            { label: "Templates and Views", slug: "core/templates" },
            { label: "Database and ORM", slug: "core/database" },
            { label: "Forms and Validation", slug: "core/forms" },
            { label: "Authentication and Security", slug: "core/security" },
            { label: "Web Profiler", slug: "core/profiler" },
          ],
        },
        {
          label: "Advanced Features",
          items: [
            {
              label: "Terminal",
              slug: "advanced_features/terminal",
            },

            { label: "Deployment", slug: "advanced_features/deployment" },
          ],
        },
        // {
        //   label: "API Reference",
        //   autogenerate: { directory: "reference" },
        // },
        // {
        //   label: "Examples",
        //   items: [
        //     // { label: "Blog Application", slug: "examples/blog" },
        //     // { label: "REST API", slug: "examples/api" },
        //     // { label: "Complete Authentication", slug: "examples/auth" },
        //   ],
        // },
      ],
      customCss: ["./framefox/src/styles/custom.css"],
    }),
  ],
});
