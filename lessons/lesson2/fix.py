#!/usr/bin/env python3
"""
Lesson 2 - Mitigation helper.

The actual fix is Node.js code in the DVSA-ORDER-MANAGER Lambda.
This script prints the exact helpers + replacement block to apply.

Usage:
    python3 fix.py
"""

JWT_HELPERS_JS = r"""
// =============================================================
// Lesson 2 Fix: JWT Signature Verification using Cognito JWKS
// Apply to: DVSA-ORDER-MANAGER Lambda -> order-manager.js
// Add these helpers AFTER: const jose = require('node-jose');
// =============================================================
const https = require('https');
let _jwksCache = { keystore: null, fetchedAt: 0 };

function resp(statusCode, bodyObj) {
    return {
        statusCode,
        headers: { "Access-Control-Allow-Origin": "*" },
        body: JSON.stringify(bodyObj)
    };
}

function fetchJson(url) {
    return new Promise((resolve, reject) => {
        https.get(url, (res) => {
            let data = "";
            res.on("data", (c) => data += c);
            res.on("end", () => {
                if (res.statusCode >= 200 && res.statusCode < 300) {
                    try { resolve(JSON.parse(data)); } catch (e) { reject(e); }
                } else {
                    reject(new Error('HTTP ' + res.statusCode));
                }
            });
        }).on("error", reject);
    });
}

async function getCognitoKeystore() {
    const now = Date.now();
    if (_jwksCache.keystore && (now - _jwksCache.fetchedAt) < 6 * 60 * 60 * 1000) {
        return _jwksCache.keystore;
    }
    const region = process.env.AWS_REGION;
    const userPoolId = process.env.userpoolid;
    const jwksUrl = `https://cognito-idp.${region}.amazonaws.com/${userPoolId}/.well-known/jwks.json`;
    const jwks = await fetchJson(jwksUrl);
    const keystore = await jose.JWK.asKeyStore(jwks);
    _jwksCache = { keystore, fetchedAt: now };
    return keystore;
}

async function verifyCognitoJwt(jwt) {
    const region = process.env.AWS_REGION;
    const userPoolId = process.env.userpoolid;
    const issuer = `https://cognito-idp.${region}.amazonaws.com/${userPoolId}`;
    const keystore = await getCognitoKeystore();
    const result = await jose.JWS.createVerify(keystore).verify(jwt);
    const claims = JSON.parse(result.payload.toString("utf8"));
    if (claims.iss !== issuer) throw new Error("bad issuer");
    if (typeof claims.exp === "number" && (Date.now() / 1000) > claims.exp) throw new Error("expired");
    if (claims.token_use && !["access", "id"].includes(claims.token_use)) throw new Error("bad token_use");
    return claims;
}
""".strip()

REPLACEMENT_BLOCK_JS = r"""
// --- Replace the vulnerable JWT parsing block with this ---

// BEFORE (vulnerable):
//   var token_sections = auth_header.split('.');
//   var auth_data = jose.util.base64url.decode(token_sections[1]);
//   var token = JSON.parse(auth_data);
//   var user = token.username;

// AFTER (fixed):
var jwt = auth_header.replace(/^Bearer\s+/i, "").trim();
if (!jwt) return callback(null, resp(401, { status: "err", msg: "missing authorization" }));
verifyCognitoJwt(jwt).then((claims) => {
    var user = claims.username || claims["cognito:username"] || claims.sub;
    // ... continue with the rest of the handler ...
}).catch((e) => {
    return callback(null, resp(401, { status: "err", msg: "invalid token" }));
});
""".strip()


def main() -> int:
    print("=" * 64)
    print(" Lesson 2 - Fix for DVSA-ORDER-MANAGER / order-manager.js")
    print("=" * 64)
    print()
    print("[1] Add these helpers near the top of order-manager.js")
    print("    (right after `const jose = require('node-jose');`):")
    print()
    print(JWT_HELPERS_JS)
    print()
    print("[2] Replace the vulnerable JWT parsing block with verified claims:")
    print()
    print(REPLACEMENT_BLOCK_JS)
    print()
    print("[3] Ensure these env vars are set on the Lambda:")
    print("      AWS_REGION   (auto-provided)")
    print("      userpoolid   (Cognito User Pool ID)")
    print()
    print("[4] Redeploy:")
    print("    zip -r order-manager.zip .")
    print("    aws lambda update-function-code \\")
    print("        --function-name DVSA-ORDER-MANAGER \\")
    print("        --zip-file fileb://order-manager.zip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
