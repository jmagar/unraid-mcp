import { defineCustomElement } from "vue";
import App from "./App.vue";
// Light-DOM custom element (shadowRoot: false) — this page isn't an isolated
// SPA, it's a classic Unraid webGUI page, so there's no benefit to shadow-DOM
// encapsulation and it lets the compiled CSS ship as an ordinary stylesheet
// the .page file links directly, rather than an inlined style string.
import "./styles/index.css";
// Aurora tokens are only consumed by Terminal.vue (real color values it reads
// via getComputedStyle for canvas rendering); the --aurora-* namespace has no
// overlap with the unraid-ui/shadcn tokens the rest of this page uses.
import "./styles/aurora-tokens.css";

const IncusSettingsApp = defineCustomElement(App, { shadowRoot: false });

if (!customElements.get("incus-settings-app")) {
  customElements.define("incus-settings-app", IncusSettingsApp);
}
