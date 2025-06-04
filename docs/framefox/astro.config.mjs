// @ts-check
import { defineConfig } from "astro/config";
import starlight from "@astrojs/starlight";

// https://astro.build/config
export default defineConfig({
  site: "https://soma-smart.github.io",
  base: "/",
  integrations: [
    starlight({
      title: "Framefox Documentation",
      description:
        "Modern Python web framework for rapidly developing robust applications",
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
          label: "Getting Started",
          items: [
            { label: "Quick Start Guide", slug: "index" },
            { label: "Installation", slug: "installation" },
          ],
        },
        {
          label: "Core Documentation",
          items: [
            { label: "Controllers", slug: "controllers" },
            { label: "Routing System", slug: "routing" },
            { label: "Templates and Views", slug: "templates" },
            { label: "Database and ORM", slug: "database" },
            { label: "Forms and Validation", slug: "forms" },
            { label: "Authentication and Security", slug: "security" },
          ],
        },
        {
          label: "Advanced Features",
          items: [
            { label: "Middleware and Events", slug: "middleware" },
            {
              label: "Services and Dependency Injection",
              slug: "services",
            },
            { label: "Terminal and Commands", slug: "terminal" },
            { label: "Web Profiler", slug: "profiler" },
            { label: "Testing", slug: "testing" },
            { label: "Deployment", slug: "deployment" },
          ],
        },
        {
          label: "API Reference",
          autogenerate: { directory: "reference" },
        },
        {
          label: "Examples",
          items: [
            // { label: "Blog Application", slug: "examples/blog" },
            // { label: "REST API", slug: "examples/api" },
            // { label: "Complete Authentication", slug: "examples/auth" },
          ],
        },
      ],
      customCss: ["./src/styles/custom.css"],
    }),
  ],
});
