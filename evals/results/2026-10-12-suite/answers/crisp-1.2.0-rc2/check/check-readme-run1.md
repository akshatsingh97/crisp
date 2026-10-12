I could not run the checker or read the rule files. Both were blocked by permissions. I checked the text by hand against the session rules. I left out rule IDs because I could not confirm them.

| Rule | Text | Fix |
|---|---|---|
| Missing facts (completeness) | "make sure that you've installed Node 18+" | Add the check command: `node --version`. Say what to do if the version is lower. |
| Missing facts (completeness) | `npm install` | State the directory to run it in (project root) and what success looks like. Add what to do if it fails. |
| Missing facts (completeness) | `npm start` | State the URL or port, and the expected output. Both are unknown, so mark them as assumptions or ask for them. |
| Vague claim, unneeded | "the app leverages a robust caching layer under the hood which seamlessly speeds things up" | Delete it from the steps. If the caching matters, move it to a separate explanation with a concrete fact. |
| Steps and explanation mixed | One paragraph holds prerequisites, install, an explanation, and start | Use a numbered list with one instruction per step. Put the explanation outside the list. |
| Sentence length (20 words max) | "You should first make sure ... you'll be good to go; the app leverages ... things up." (about 45 words) | Split into short sentences: "Install Node 18 or later." "Run `npm install`." |
| Semicolon | "good to go; the app" | Use a full stop. |
| Contractions | "It's", "you've", "you'll" | Write "It is", "you have", "you will", or drop them. |
| Modal verb | "You should first" | Use the imperative: "First, install Node 18+." |
| Filler words | "really easy", "simply", "robust", "seamlessly", "under the hood" | Delete them. |
| Plain word | "leverages" | Use "uses". |
| Closer | "Hope this helps!" | Delete it. |
| Exclamation and condition order | "It's really easy ... running!" | Delete the sentence. It gives no fact. |
| Condition order | "Run `npm start` if you want to start the server." | Write "To start the server, run `npm start`." |

Score: I have no checker score because the script did not run. By hand, the text fails on almost every rule: long sentences, filler, contractions, a semicolon, a closer, and no expected results or failure handling.

Do you want me to apply the fixes?
