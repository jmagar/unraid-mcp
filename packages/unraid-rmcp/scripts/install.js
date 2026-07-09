#!/usr/bin/env node
"use strict";
const fs = require("node:fs");
const http = require("node:http");
const https = require("node:https");
const os = require("node:os");
const path = require("node:path");
const { spawnSync } = require("node:child_process");
const { binaryPath, downloadUrl, installRoot, releaseVersion, targetFor } = require("../lib/platform");
function log(message) { process.stderr.write(`unraid-rmcp: ${message}\n`); }
function download(url, destination) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith("http:") ? http : https;
    const request = client.get(url, (response) => {
      if ([301, 302, 303, 307, 308].includes(response.statusCode)) { response.resume(); download(response.headers.location, destination).then(resolve, reject); return; }
      if (response.statusCode !== 200) { response.resume(); reject(new Error(`download failed (${response.statusCode}) from ${url}`)); return; }
      const file = fs.createWriteStream(destination, { mode: 0o600 });
      response.pipe(file);
      file.on("finish", () => file.close(resolve));
      file.on("error", reject);
    });
    request.on("error", reject);
  });
}
function extract(archive, destination) {
  fs.rmSync(destination, { recursive: true, force: true });
  fs.mkdirSync(destination, { recursive: true });
  const result = spawnSync("tar", ["-xzf", archive, "-C", destination], { encoding: "utf8" });
  if (result.status !== 0) throw new Error((result.stderr || result.stdout || "tar extraction failed").trim());
}
async function main() {
  if (process.env.UNRAID_RMCP_SKIP_DOWNLOAD === "1") { log("skipping binary download because UNRAID_RMCP_SKIP_DOWNLOAD=1"); return; }
  const target = targetFor();
  const destination = binaryPath();
  if (fs.existsSync(destination)) { log(`${path.basename(destination)} already installed for ${releaseVersion()}`); return; }
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "unraid-rmcp-install-"));
  const archive = path.join(tempDir, target.asset);
  try {
    const url = downloadUrl(target);
    log(`downloading ${url}`);
    await download(url, archive);
    extract(archive, installRoot());
    fs.chmodSync(destination, 0o755);
    log(`installed ${destination}`);
  } finally { fs.rmSync(tempDir, { recursive: true, force: true }); }
}
main().catch((error) => { log(error.message); process.exitCode = 1; });
