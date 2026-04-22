## Screenshots — where to place every image

One folder per lesson (Lesson1 … Lesson10). Each folder's `brief.txt` explains
the lesson in one paragraph; `screenshots.txt` (only in lessons 1, 2, 7, 9)
lists every required screenshot, the exact filename to save it as, what the
image must show, and the one-line caption you'll paste into the report.

Naming convention for every file in this tree:

    NN-short-description.png       (zero-padded, kebab-case, PNG only)

Keep each file under ~2 MB. Sanitize before committing — blur:

- Real 12-digit AWS account IDs
- Real API Gateway IDs (e.g. `abc123xyz.execute-api...`)
- Cognito User Pool / App Client IDs
- Full JWTs (show first 6 and last 6 chars, replace middle with `...`)
- Real emails, phone numbers, student IDs
- Browser bookmarks, other tabs, Slack/email notifications

Preview on macOS: open the PNG → Tools → Annotate → Rectangle (filled, black).

`loot/` holds the same evidence but sanitized and committed; `screenshots/` is
where you stage raw captures while writing the report. Only sanitized copies
should ever be pushed.
