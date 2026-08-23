# Chat Security Notes (GitHub Pages Only)

This site is deployed as static frontend code on GitHub Pages.  
Because of this, any API key used directly from browser JavaScript is eventually discoverable.

## Current Mode

- `assets/js/chat.js` calls OpenRouter directly from the browser.
- The key is injected during GitHub Actions deploy using `secrets.OPENROUTER_API_KEY`.
- This setup is functional but not fully secure against determined scraping/abuse.

## Least-Risk Controls Implemented

1. **Dedicated key**
   - Use a key only for this portfolio (never reuse development/personal keys).

2. **Usage limits in code**
   - Fixed model in frontend.
   - Low `max_tokens` per response to limit spend.

3. **Frontend anti-abuse controls**
   - Per-session message cap.
   - Local rate limiting.
   - Duplicate-message blocking.
   - Prompt-injection pattern blocking.

## Required OpenRouter Dashboard Controls

1. **Hard spend cap**
   - Set strict monthly limit for this key.

2. **Low rate limits**
   - Keep conservative request/token limits.

3. **Monitoring and rotation**
   - Monitor usage regularly.
   - Rotate/revoke key immediately on suspicious spikes.

## Important Limitation

Without a backend proxy, this cannot be made non-leakable.  
These controls reduce blast radius but do not eliminate key exposure risk.
