/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_MOBILERUN_API_KEY?: string;
    readonly VITE_GATEWAY_URL?: string;
    readonly VITE_IRONCLAW_API_TOKEN?: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}

