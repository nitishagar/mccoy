import { docsLoader } from "@astrojs/starlight/loaders";
import { docsSchema } from "@astrojs/starlight/schema";
import { defineCollection } from "astro:content";

// Starlight 0.34+ requires an explicit docs collection with the docsLoader. All markdown under
// src/content/docs/ is served as the docs site.
const docs = defineCollection({ loader: docsLoader(), schema: docsSchema() });

export const collections = {
  docs,
};
