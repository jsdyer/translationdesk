# Translation Desk

[Open Translation Desk](https://coolcode.ca/translationdesk/) — translate on your device or through a LibreTranslate server you choose, then review paired passages and export a portable project.

<!-- coolcode:guide -->
Choose source and target language codes, prepare the browser language pair, then select **Translate**. Preparation may download a language pack; it does not upload your source text. The original and editable translation are paired by paragraph order, so review their alignment and wording. If this browser lacks the Translator API, use your LibreTranslate server or paste an existing translation for local review. **Save project** keeps the texts and glossary; nothing is saved automatically and server keys are excluded.
<!-- /coolcode:guide -->

## Two translation paths, one review workspace

1. **On this device:** a supported desktop browser exposing the [Translator API](https://developer.chrome.com/docs/ai/translator-api). Current Chrome documentation describes desktop support from Chrome 138; the app uses feature detection instead of assuming a version is sufficient. Mobile browsers and browsers without this API cannot use this path. Language pairs depend on browser/model support.
2. **My LibreTranslate server:** enter the base HTTPS URL of an instance you operate or are authorized to use. Optional server keys remain in this tab. The explicit checkbox and Translate action send source paragraphs to `/translate` with `format: "text"`. The page does not choose a public demonstration service.
3. **Review & export:** works without either translation engine. Paste original and translated text, or open a previous project; inspect paired paragraphs, check literal glossary terms and save text, CSV or JSON.

An engine failure or cancellation preserves the previous complete translation. Paragraphs are processed sequentially and the result is applied only when all paragraphs succeed. By default the source may contain 12,000 characters, with paragraphs up to 3,000. Blank lines define paragraph boundaries. The app does not claim semantic alignment or certified accuracy; names, tone, factual details and important wording need human review.

Browser models download only after **Prepare / download language pair** is selected. Preparation has a three-minute limit and may be cancelled. Text is not included in model preparation. The browser manages its own model storage. On-device translation uses the browser's implementation; this app does not silently substitute a remote API.

## Expand or customize

Edit `web/config.json`:

```json
{
  "defaultSource": "en",
  "defaultTarget": "fr",
  "libreTranslateEndpoint": "https://your-translation.example",
  "maxCharacters": 12000,
  "maxParagraphCharacters": 3000,
  "requestTimeoutSeconds": 60
}
```

Leave `libreTranslateEndpoint` empty to let each visitor choose their own server. It is currently empty because no shared Brix endpoint has been configured. Never put a private key in this file. A shared server needs appropriate authentication and rate limits; a private owner key must not become a public browser secret.

The `languages` list only supplies suggestions; any valid supported language code can be typed directly. To add Polish, append `{"code":"pl","name":"Polish"}`. The browser or server must have the corresponding models. `examples` contains editable starting texts with `id`, `name`, `source`, `target` and `text`. Add any extra example rather than editing application logic. A normal push to `main` checks and publishes config changes; there is no scheduled data refresh.

The application caps configured source length at 60,000 characters and request timeout at 300 seconds. These are explicit resource safeguards, independent of the starter language list. Imported older projects do not require their languages to be in the current suggestions. Saved project content is validated and rendered as text.

## Connect LibreTranslate on Brix

Follow [LibreTranslate's installation guide](https://docs.libretranslate.com/guides/installation/) for its Docker or production Python setup. Load the language models you need (for example `en,fr` with `--load-only en,fr`), retain model downloads on persistent storage, and put the service behind your HTTPS reverse proxy. The public app must be able to reach that URL from the visitor's browser. Configure CORS to allow `https://coolcode.ca` and handle POST/preflight requests. Do not expose an unbounded anonymous translation service accidentally; configure authentication/quotas to match its intended audience.

Use **Check server languages** to test `/languages`; it sends no source text or key. It verifies a reachable language list, not that every possible pair is installed. Then choose the server engine, enter a personal key only if the server requires one, allow text transmission and translate a short test. Typical failures are unavailable models, authentication, rate limits, or a proxy/CORS rule. Server errors retain the last good translation.

## Privacy and exports

The app itself stores no text in localStorage, cookies or a backend. Imported text and projects stay in memory. The native Translator API processes text on the device; browser-managed model downloads contact the browser provider. LibreTranslate sends only the source paragraphs, requested languages and optional key to the explicitly selected endpoint, with no cookies and no referrer. Glossary terms remain local and are not sent to either translation engine.

A project JSON contains both texts, their language codes, glossary and translation date/engine; it never contains a server key or the server URL. CSV pairs paragraphs in their current order and neutralizes spreadsheet formula prefixes. Text exports contain only the target text. Do not share a project containing private text unintentionally. Shared CoolCode metrics record aggregate page opens, not workspace content.

## Sources and verification

- [Chrome Translator API](https://developer.chrome.com/docs/ai/translator-api), feature-detected and prepared by explicit user action.
- [LibreTranslate API](https://docs.libretranslate.com/guides/api_usage/), `/languages` and `/translate` contract.

```sh
node --test tests/*.test.mjs
python3 -m unittest discover -s tests -v
python3 scripts/build.py
```

The build is offline and dependency-free. CI browser checks exercise local review/export, a controlled Translator API test double, server permission handling, cancellation/error preservation and mobile layout. That test double verifies integration behavior; it does not evaluate translation quality or claim that the CI browser has a downloaded native model. A real browser/model or configured live server is needed for end-to-end machine-translation verification.

Browser verification on 2026-11-23: desktop Chrome successfully downloaded/prepared the native English–French pair and translated “The library is open today.” to “La bibliothèque est ouverte aujourd’hui.” using the real on-device Translator API. Other browsers and language pairs remain capability-dependent.
