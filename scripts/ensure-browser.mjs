// Déploie le Chromium embarqué (@sparticuz/chromium) de façon idempotente.
// Le sandbox n'a pas accès aux CDN Chrome officiels ; ce paquet npm contient le
// binaire + les libs AL2023 (nss/nspr) dans son tarball (hôte autorisé : npmjs).
// Astuce : AWS_EXECUTION_ENV déclenche l'extraction du bundle al2023.tar.br.
import { existsSync, rmSync } from "node:fs";

const CHROME = "/tmp/chromium";
const NSS = "/tmp/al2023/lib/libnss3.so";

if (existsSync(CHROME) && !existsSync(NSS)) {
  // extraction partielle antérieure : on repart propre
  rmSync(CHROME, { force: true });
}

process.env.AWS_EXECUTION_ENV = process.env.AWS_EXECUTION_ENV || "AWS_Lambda_nodejs22.x";
const { default: chromium } = await import("@sparticuz/chromium");
const p = await chromium.executablePath();
console.log(p);
