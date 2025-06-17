// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
  site: "https://soma-smart.github.io",
  base: "/framefox",
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
        baseUrl: "https://github.com/soma-smart/framefox/edit/main/docs/framefox/src/content/docs/",
      },
      lastUpdated: true,
      sidebar: [
        {
          label: "Getting Started",
          items: [
            { label: "Introduction", slug: "framefox/introduction" },
            { label: "Quick Start Guide", slug: "framefox/quick_start" },
            { label: "Installation", slug: "framefox/installation" },
          ],
        },
        {
          label: "Core Documentation",
          items: [
            { label: "Controllers", slug: "framefox/core/controllers" },
            { label: "Routing System", slug: "framefox/core/routing" },
            { label: "Templates and Views", slug: "framefox/core/templates" },
            { label: "Database and ORM", slug: "framefox/core/database" },
            { label: "Forms and Validation", slug: "framefox/core/forms" },
            { label: "Authentication and Security", slug: "framefox/core/security" },
            { label: "Web Profiler", slug: "framefox/core/profiler" },
          ],
        },
        {
          label: "Advanced Features",
          items: [
            {
              label: "Terminal",
              slug: "framefox/advanced_features/terminal",
            },

            { label: "Deployment", slug: "framefox/advanced_features/deployment" },
          ],
        },
        // {
        //   label: "API Reference",
        //   autogenerate: { directory: "reference" },
        // },
        // {
        //   label: "Examples",
        //   items: [
        //     // { label: "Blog Application", slug: "framefox/examples/blog" },
        //     // { label: "REST API", slug: "framefox/examples/api" },
        //     // { label: "Complete Authentication", slug: "framefox/examples/auth" },
        //   ],
        // },
      ],
      customCss: ["./src/styles/custom.css"],
    }),
  ],
});
