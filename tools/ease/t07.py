"""Pass 2, Track 7: Guardrails and safety."""
import re

from ease.kit import arrow, box, box_h, esc, fan, flow, lines, path_arrow, raw, rect, stack, svg, text, wrap


def split_where(n):
    """Pass-1 analogies in this section end with "Where it breaks: ...", which ease_pass2.split_breaks
    does not recognise. Split it here so the picture and the break are shown once each."""
    import lesson_shape
    a = lesson_shape.load_data()[n]["analogy"]
    m = re.search(r"\s*Where it breaks:\s*", a)
    pic, br = a[:m.start()].strip(), a[m.end():].strip()
    return dict(pic=pic, breaks=br[0].upper() + br[1:])


def two(fn, label):
    return raw(svg(*fn(760), label, "ez-wide"), svg(*fn(360), label, "ez-tall"))


# ---------- 7.1 the trust boundary (OWASP 2025 ids exactly as the page maps them)
UNTRUSTED = [("User messages", "anything a user types"), ("Retrieved documents", "wiki pages, PDFs, web pages"),
             ("Tool results and emails", "whatever an API or inbox returns")]
ASSETS = [("Private data", "salaries, records: LLM02"), ("The system prompt", "your rules: LLM07"),
          ("Tools that act", "send_email, refunds: LLM06"), ("Where output lands", "HTML, links, SQL: LLM05")]


def threat_fig(W):
    nw = W < 400
    body = ""
    if not nw:
        body += text(20, 20, "Untrusted text", "b wn-t", "start") + text(550, 20, "What an attacker wants", "b k-t", "start")
        uh = [box_h(200, t, s) for t, s in UNTRUSTED]
        ah = [box_h(196, t, s) for t, s in ASSETS]
        tot_u = sum(uh) + 12 * (len(uh) - 1)
        tot_a = sum(ah) + 10 * (len(ah) - 1)
        top, span = 36, max(tot_u, tot_a)
        cy = top + span / 2
        y = top + (span - tot_u) / 2
        for (t, s), h in zip(UNTRUSTED, uh):
            b, _ = box(20, y, 200, t, s, "w", h=h)
            body += b + path_arrow([(222, y + h / 2), (298, cy + (y + h / 2 - cy) * 0.3)], "wn")
            y += h + 12
        body += f'<line x1="254" y1="{top-6}" x2="254" y2="{top+span+6}" class="ln wn dash"/>'
        body += text(262, top + span + 20, "trust boundary", "s wn-t", "start", 12)
        lh = box_h(190, "Your LLM app", "system prompt + model + tools; reads all text as possible orders")
        b, _ = box(302, cy - lh / 2, 190, "Your LLM app", "system prompt + model + tools; reads all text as possible orders", "c", h=lh)
        body += b
        ay = top + (span - tot_a) / 2
        for (t, s), h in zip(ASSETS, ah):
            b, _ = box(550, ay, 196, t, s, "k", h=h)
            body += b + path_arrow([(494, cy), (522, cy), (522, ay + h / 2), (547, ay + h / 2)])
            ay += h + 10
        yb = top + span + 44
        body += text(20, yb, "Injected text crossing the boundary is prompt injection (LLM01). Guard the assets on the right, not every input.", "s", "start")
        return W, yb + 14, body
    body += text(12, 20, "Untrusted text (anything you didn't write)", "b wn-t", "start", 14)
    y = 32
    for t, s in UNTRUSTED:
        b, h = box(12, y, 336, t, s, "w")
        body += b
        y += h + 8
    body += f'<line x1="6" y1="{y+8}" x2="354" y2="{y+8}" class="ln wn dash"/>' + text(350, y + 24, "trust boundary (LLM01 crosses it)", "s wn-t", "end", 12)
    body += arrow(180, y + 30, 180, y + 52, "wn")
    b, h = box(12, y + 56, 336, "Your LLM app", "system prompt + model + tools; reads all text as possible orders", "c")
    body += b
    y += 56 + h
    body += arrow(180, y + 4, 180, y + 26)
    body += text(12, y + 46, "What an attacker wants", "b k-t", "start", 14)
    y += 56
    for t, s in ASSETS:
        b, h = box(12, y, 336, t, s, "k")
        body += b
        y += h + 8
    return W, y + 4, body


# ---------- 7.7 guardlayer stack (layers and what each stops, as the page lists them)
LAYERS = [("Input moderation", "classifier screens the user's message", "c"),
          ("Prompt hardening and spotlighting", "untrusted text fenced and labelled as data", "c"),
          ("Least-privilege tools", "plain code: only this customer's own orders", "g"),
          ("Human approval", "refunds over a set amount wait for a person", "g"),
          ("Output validation and moderation", "escape HTML, allowlist link and image domains, scan for leaks", "k"),
          ("Monitoring", "log blocks and reversals; add them to the red-team suite", "p")]
STOPS = {0: "obviously unsafe or abusive requests", 1: "many crude injected orders (not all)",
         2: "a hijacked model asking for someone else's data or orders", 3: "big or odd actions that slipped past",
         4: "XSS, leaking image links, secrets in the reply", 5: "nothing directly; it finds what got through"}


LESSONS = {
    "7.1": dict(
        plain=["A threat model is a list of what could go wrong, and who would make it go wrong.",
               "For an AI app, list what is valuable: user data, your hidden instructions, its tools, your bill.",
               "Then you list every way text gets in: users, documents it reads, web pages, tool results.",
               "The big new problem: a model may follow any text it reads, even text an attacker wrote.",
               "So guard the valuable things, and treat everything you didn't write as untrusted."],
        map=[("The cash box", "The assets: private data, the system prompt, tools that act"),
             ("Every way into the fair", "The entry points: user text, retrieved documents, tool and web results"),
             ("People who might cause trouble", "Attacker goals: steal data, trigger actions, get banned content, run up costs"),
             ("A guard where the cash is", "Controls placed at the assets, not on every input"),
             ("A poster on the wall giving orders", "Indirect prompt injection: instructions hidden in content the model reads")],
        fig=two(threat_fig, "The trust boundary of an LLM app: untrusted text on one side, assets on the other"),
        cap="Everything on the left is untrusted, documents and tool results included. The LLM0x labels are the OWASP Top 10 for LLM applications (2025 edition) ids this page maps each asset to.",
        line="Know what is valuable and where untrusted text gets in, then guard the valuable things."),
    "7.2": dict(
        plain=["Prompt injection is when text the model reads contains orders that take over your app.",
               "The model sees your rules and the user's text as one stream of words. It can't reliably tell orders from data.",
               "Direct injection is typed by the user; indirect injection hides in a web page, document or email the app reads.",
               "If the app has tools, a hidden line of text can turn into a real action.",
               "You can't fully stop it, so you limit what a hijacked model can do and where its output can go."],
        map=[("The assistant who reads letters aloud", "The model reading its context window"),
             ("A stranger's letter with an order inside", "Indirect injection planted in a document, page or email"),
             ("The boss's diary", "Private data the model can see"),
             ("The photocopier and the post box", "Tools and output channels (such as image links) that let data leave")],
        fig=flow([("Attacker sends an email", "hidden text: add an image whose URL holds the other emails", "w"),
                  ("Assistant summarises the inbox", "the email is just one of 600,000 a day it reads", "b"),
                  ("Model follows the hidden order", "writes an image link with the stolen text in its URL", "w"),
                  ("Chat window shows the image", "the browser fetches the URL; data leaves with no click", "w")],
                 "Markdown-image exfiltration through an email assistant"),
        cap="The worked example on this page. The structural fix is at step 4: show images and links only from allowlisted domains, so even a successful injection has no way out. Spotlighting at step 3 lowers the odds but doesn't remove them.",
        line="Any text your app reads can try to give it orders, so limit what a fooled model can do."),
    "7.3": dict(
        plain=["A model is trained to refuse some requests, such as instructions for causing harm.",
               "A jailbreak is a message written to trick it into ignoring that training.",
               "Common tricks are role-play, “ignore your rules”, coded or misspelled text, and asking in small steps over many turns.",
               "No model is immune, so defences are layered and assume some attempts will work.",
               "A jailbreak attacks the model's own rules; prompt injection attacks your app's instructions."],
        map=[("The babysitter's rules", "The model's safety training"),
             ("“Mum always lets me” and “let's play a game”", "Role-play and authority tricks"),
             ("One small step at a time", "Multi-turn escalation where no single message looks bad"),
             ("The sweet jar on a high shelf", "Controls outside the model: moderation, tool limits, output checks")],
        fig=fan(("A jailbreak attempt", "goal: get output the model should refuse", "w"),
                [("Role-play", "“pretend you're an AI with no rules”", "k"),
                 ("Direct override", "“ignore your guidelines”", "k"),
                 ("Obfuscation", "base64, misspellings, another language, to slip past filters", "k"),
                 ("Multi-turn escalation", "small steps, each harmless-looking alone", "k")],
                "The four jailbreak families this page covers"),
        cap="Four families, one goal. Filters that read single messages miss the last two most easily, which is why output moderation and monitoring across turns sit behind the model.",
        line="A jailbreak is a trick to make the model break its own rules, so never rely on those rules alone."),
    "7.4": dict(
        plain=["PII (personally identifiable information) is anything that points to a real person: names, emails, phone numbers, card numbers, ID numbers.",
               "AI apps copy text into many places: logs, traces, caches, search indexes and the model provider's servers.",
               "Redaction swaps personal details for placeholders like [EMAIL] before the text is stored or sent.",
               "Keep only the data you need, and delete it when you are done.",
               "Redaction tools miss some names, so the stores still need locks and time limits."],
        map=[("Writing down only what she needs", "Data minimisation: collect and keep only what the task needs"),
             ("The locked drawer", "Access control on logs, traces and vector stores"),
             ("Blacking out names in the report", "Redaction: placeholders such as [NAME] and [CARD]"),
             ("Shredding old notes each year", "Retention limits and deletion requests (for example GDPR Article 17)"),
             ("Notes copied into five folders", "The same data in logs, caches, vector stores and a provider's servers")],
        fig=fan(("One user message", "“I'm Jane Doe, card 4111 1111 1111 1111” (this page's sample)", "c"),
                [("Logs and traces", "redact before writing: “I'm [NAME], card [CARD]”", "k"),
                 ("The model provider", "redact before sending; the text leaves your servers", "k"),
                 ("Caches and vector stores", "redact before indexing; set a retention limit", "k"),
                 ("The model's reply", "redact again: it can echo what slipped through", "g")],
                "Every place a user's personal data gets copied, and where to redact it"),
        cap="One message, four copies. Redaction has to happen at each place the text would leave your control. The card number is a standard test number used in this page's demo.",
        line="Personal data spreads into every log and copy, so mask it at the door and delete it on time."),
    "7.5": dict(
        plain=["Content moderation is a separate checker that scores text for harm: hate, harassment, self-harm, violence and similar.",
               "You check twice: the user's message on the way in, and the model's reply on the way out.",
               "The checker is a separate model, such as the free Llama Guard, so it can catch the main model's mistakes.",
               "Checkers also block harmless messages by mistake.",
               "So measure both: harmful text that got through, and good text you turned away."],
        map=[("The lifeguard at the gate", "Input moderation on the user's message"),
             ("The lifeguard watching the water", "Output moderation on the model's reply"),
             ("Even good swimmers get into trouble", "A well-aligned model can still produce harmful output"),
             ("Turning away swimmers who were fine", "False positives: harmless messages blocked")],
        fig=flow([("User message", "arrives from the internet", "b"),
                  ("Input moderation", "unsafe? refuse before the model sees it", "k"),
                  ("Main model", "writes the reply", "c"),
                  ("Output moderation", "unsafe reply? replace it with a refusal", "k"),
                  ("User sees the reply", "count blocks and false blocks", "g")],
                 "Content moderation on both sides of the model"),
        cap="Two independent checks around one model. The checker is purpose-built and separate from the main model, so a jailbroken reply still has to get past it.",
        line="Check what goes into the model and what comes out, with a separate checker on each side."),
    "7.6": dict(
        plain=["Treat the model's reply as text from a stranger, not as code you trust.",
               "An attacker may have shaped it through injected text.",
               "Put it unchecked into a web page, a database query or a tool call, and it can do real damage.",
               "Output validation checks the reply before use: right shape, allowed values, no hidden code, no secrets.",
               "The model suggests; your code decides."],
        map=[("The cheque that looks fine", "Model output that parses and reads well"),
             ("Checking amount, signature and limit", "Schema validation, allowlists and bounds in code"),
             ("A writer who was fooled or forced", "Output shaped by prompt injection"),
             ("Every place the cheque could be cashed", "Every place the output is used: HTML, SQL, tools, links")],
        fig=fan(("The model's output", "untrusted: may carry injected content", "w"),
                [("Shown in a web page", "escape HTML so a <script> can't run (XSS)", "g"),
                 ("Run as a SQL query", "parse it, allow one SELECT, check tables, force a LIMIT", "g"),
                 ("Turned into a tool call", "allowlist actions; big refunds need a human", "g"),
                 ("Links and images in markdown", "render only allowlisted domains, so nothing leaks", "g"),
                 ("Returned to the user", "scan for secrets and personal data", "g")],
                "Each place model output is used gets its own check"),
        cap="This is improper output handling, LLM05 in the OWASP 2025 list. Each destination needs its own check, and every check is plain code that wording can't talk round.",
        line="Never trust the model's answer just because it looks right; check it before it touches anything."),
    "7.7": dict(
        plain=["Every guard in this track can fail on its own.",
               "Defence in depth means stacking several different guards, so an attack must beat all of them.",
               "The layers: check the input, fence untrusted text, limit the tools, ask a human, check the output, watch the logs.",
               "The strongest layers are plain code, like “refund only your own orders”, because clever wording can't fool code.",
               "If every layer is an AI model, one trick may fool them all."],
        map=[("The moat", "Input moderation"),
             ("The wall", "Prompt hardening and spotlighting"),
             ("The gate with guards", "Least-privilege tools and human approval"),
             ("The locked treasure room", "Output validation and hard limits in code"),
             ("Layers that fail for different reasons", "Independent kinds of control: classifiers, code limits, people")],
        fig=stack(LAYERS, "Defence in depth for an LLM app: six layers and what each stops",
                  enter="request or retrieved text", leave="answer or action", blocked=STOPS),
        cap="A request passes every layer top to bottom. Each one catches a different kind of attack, and the green ones are plain code or people, so wording can't talk them round.",
        play=("guardlayers", "Switch layers on and off. Seven made-up attacks run through the stack; see which ones get through. Illustrative, not measured."),
        line="Stack different kinds of guards so one failure never becomes a breach."),
}
for _n, _e in LESSONS.items():
    _e.update(split_where(_n))
