import starlight from "@astrojs/starlight";
import expressiveCode from "astro-expressive-code";
import { defineConfig } from "astro/config";

export default defineConfig({
  site: "https://nitishagar.github.io",
  integrations: [
    expressiveCode({
      style: {
        borderRadius: "0px",
        codeFontFamily: '"IBM Plex Mono", ui-monospace, monospace',
        uiFontFamily: '"IBM Plex Mono", ui-monospace, monospace',
      },
    }),
    starlight({
      title: "McCoy",
      social: [
        { label: "GitHub", icon: "github", href: "https://github.com/nitishagar/mccoy" },
      ],
      sidebar: [
        { label: "Overview", link: "/overview/" },
        { label: "Install", link: "/install/" },
        { label: "Quickstart", link: "/quickstart/" },
        { label: "Rules", autogenerate: { directory: "rules" } },
        { label: "CLI reference", link: "/cli/" },
        { label: "Fix loop", link: "/fix-loop/" },
        { label: "Fixtures", link: "/fixtures/" },
        { label: "Changelog", link: "/changelog/" },
      ],
      customCss: ["./src/styles/tokens.css", "./src/styles/custom.css"],
    }),
  ],
});
