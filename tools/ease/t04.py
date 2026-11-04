"""Pass 2, Track 4: Agents."""
from ease.kit import arrow, box, box_h, compare, fan, flow, lines, path_arrow, raw, rect, stack, svg, text, wrap


# ---------- 4.3 the agent loop: think -> act -> observe -> budget check, with two exits
def loop_svg():
    out = []
    # ---- wide
    W = 760
    nodes = {
        "goal": (20, 112, 130, "Goal", "“Has order 4417 shipped?”", "b"),
        "think": (200, 112, 160, "1. Think", "model reads all messages, picks the next move", "a"),
        "act": (430, 16, 170, "2. Act", "tool call, e.g. get_order(4417)", "k"),
        "obs": (430, 214, 170, "3. Observe", "your code runs it; the result is appended", "c"),
        "guard": (200, 300, 160, "Budget check", "steps used < max_steps?", "p"),
        "final": (630, 112, 112, "Final answer", "no tool call: the loop ends", "g"),
        "stop": (20, 300, 130, "Stopped", "“hit max steps”", "w"),
    }
    hs = {k: box_h(v[2], v[3], v[4], 14) for k, v in nodes.items()}
    body = ""
    for k, (x, y, w, t, s, tone) in nodes.items():
        b, _ = box(x, y, w, t, s, tone, h=hs[k], size=14)
        body += b

    def mid(k, side):
        x, y, w = nodes[k][:3]
        h = hs[k]
        return {"l": (x, y + h / 2), "r": (x + w, y + h / 2), "t": (x + w / 2, y), "b": (x + w / 2, y + h)}[side]
    g, t_ = mid("goal", "r"), mid("think", "l")
    body += arrow(g[0] + 3, g[1], t_[0] - 3, t_[1])
    tr = mid("think", "t")
    al = mid("act", "l")
    body += path_arrow([(tr[0], tr[1] - 2), (tr[0], al[1]), (al[0] - 3, al[1])], "ac")
    ab, ot = mid("act", "b"), mid("obs", "t")
    body += arrow(ab[0], ab[1] + 3, ot[0], ot[1] - 3, "ac")
    ol, gr = mid("obs", "l"), mid("guard", "r")
    body += path_arrow([(ol[0] - 2, ol[1]), (gr[0] + 30, ol[1]), (gr[0] + 30, gr[1]), (gr[0] + 3, gr[1])], "ac")
    gt, tb = mid("guard", "t"), mid("think", "b")
    body += arrow(gt[0], gt[1] - 3, tb[0], tb[1] + 3, "ok")
    body += text(gt[0] + 8, (gt[1] + tb[1]) / 2 + 5, "yes: next step", "s ok-t", "start")
    gl, sr = mid("guard", "l"), mid("stop", "r")
    body += arrow(gl[0] - 3, gl[1], sr[0] + 3, sr[1], "wn")
    body += text((gl[0] + sr[0]) / 2, gl[1] - 8, "no", "s wn-t")
    trr, fl = mid("think", "r"), mid("final", "l")
    body += arrow(trr[0] + 3, trr[1], fl[0] - 3, fl[1], "ok")
    body += text((trr[0] + fl[0]) / 2 + 40, trr[1] - 8, "answer ready", "s ok-t")
    H = max(nodes["guard"][1] + hs["guard"], nodes["stop"][1] + hs["stop"]) + 14
    out.append(svg(W, H, body, "The agent loop: think, act, observe, check the step budget, repeat", "ez-wide"))
    # ---- tall: one column with the loop line on the left, exits on the right
    W2, x, w, xr, wr = 360, 30, 200, 244, 104
    col = [("goal", "Goal", "“Has order 4417 shipped?”", "b"), ("think", "1. Think", "model picks the next move", "a"),
           ("act", "2. Act", "tool call get_order(4417)", "k"), ("obs", "3. Observe", "result appended to messages", "c"),
           ("guard", "Budget check", "steps used < max_steps?", "p")]
    y, pos, body = 12, {}, ""
    for i, (k, t, s, tone) in enumerate(col):
        b, hh = box(x, y, w, t, s, tone, size=13)
        body += b
        pos[k] = (y, hh)
        if i < len(col) - 1:
            body += arrow(x + w / 2, y + hh + 2, x + w / 2, y + hh + 24, "ac" if k in ("think", "act", "obs") else "")
        y += hh + 26
    ty, th = pos["think"]
    gy, gh = pos["guard"]
    body += path_arrow([(x - 2, gy + gh / 2), (12, gy + gh / 2), (12, ty + th / 2), (x - 3, ty + th / 2)], "ok")
    body += (f'<text x="22" y="{(gy+ty)/2+th/2:g}" text-anchor="middle" class="s ok-t" '
             f'transform="rotate(-90 22 {(gy+ty)/2+th/2:g})">yes: next step</text>')
    b, fh = box(xr, ty + th / 2 - 30, wr, "Final answer", "no tool call", "g", size=13)
    body += b + arrow(x + w + 3, ty + th / 2, xr - 3, ty + th / 2, "ok")
    b, sh = box(xr, gy + gh / 2 - 30, wr, "Stopped", "hit max steps", "w", size=13)
    body += b + arrow(x + w + 3, gy + gh / 2, xr - 3, gy + gh / 2, "wn")
    out.append(svg(W2, max(y - 26, gy + gh / 2 + 30 + sh / 2) + 14, body, "The agent loop: think, act, observe, check the step budget, repeat", "ez-tall"))
    return raw(*out)


# ---------- 4.6 one MCP tool call as a sequence diagram (stateless 2026-07-28 spec)
ACTORS = [("Host app + model", "a"), ("MCP client", "c"), ("MCP server", "k"), ("Order system", "d")]
MSGS = [  # (from, to, label, kind)
    (1, 2, "tools/list: what do you offer?", "ac"),
    (2, 1, "tool get_order(order_id) + its schema", ""),
    (1, 0, "schema handed to the model as a tool", ""),
    (0, 1, "model asks: get_order(“4417”)", "ac"),
    (1, 2, "tools/call get_order {order_id: 4417}", "ac"),
    (2, 3, "server's own code queries the system", "ac"),
    (3, 2, "row: shipped, DHL", ""),
    (2, 1, "result: “shipped, DHL”", ""),
    (1, 0, "appended as a tool result; model answers", "ok"),
]


def mcp_svg():
    out = []
    for W, cls, narrow in ((760, "ez-wide", False), (360, "ez-tall", True)):
        n = len(ACTORS)
        m = 12 if narrow else 20
        cw = (W - 2 * m) / n
        xs = [m + cw * i + cw / 2 for i in range(n)]
        body = ""
        top = 12
        hh = 48 if narrow else 40
        for (name, tone), x in zip(ACTORS, xs):
            bw = cw - (8 if narrow else 20)
            body += rect(x - bw / 2, top, bw, hh, tone, rx=8)
            if narrow:
                parts = wrap(name, bw - 8, 12, bold=True)
                body += lines(x, top + (hh - len(parts) * 15) / 2 + 12, parts, "b", size=12, lh=15)
            else:
                body += text(x, top + 25, name, "b", size=14)
        y0 = top + hh + 26
        step = 40 if not narrow else 44
        yend = y0 + len(MSGS) * step + 6
        for x in xs:
            body += f'<line x1="{x:g}" y1="{top+hh}" x2="{x:g}" y2="{yend:g}" class="grid dash"/>'
        for k, (a, b, lab, kind) in enumerate(MSGS):
            y = y0 + k * step
            xa, xb = xs[a], xs[b]
            d = 1 if xb > xa else -1
            label = f"{k+1}. {lab}"
            if narrow:
                body += text(m, y + 6, label, "s", "start", 12)
                body += arrow(xa + d * 4, y + 22, xb - d * 4, y + 22, kind)
            else:
                lx = (xa + xb) / 2
                body += text(lx, y + 8, label, "s", size=13)
                body += arrow(xa + d * 4, y + 18, xb - d * 4, y + 18, kind)
        note = "Spec 2026-07-28: no initialize handshake; every request carries its own protocol version and capabilities."
        nl = wrap(note, W - 2 * m, 13)
        body += lines(m, yend + 22, nl, "s m", "start", 13, 17)
        out.append(svg(W, yend + 22 + len(nl) * 17, body, "One MCP tool call: host, client, server and back", cls))
    return raw(*out)


LESSONS = {
    "4.1": dict(
        plain=["A chatbot answers from what it already knows, in one reply.",
               "An agent works toward a goal. It can use tools, such as a search, a calculator or your database.",
               "It looks at what each tool returns and decides the next step, again and again, until the job is done.",
               "That repeating cycle is called the agent loop.",
               "More freedom means more power and more ways to fail, so give an agent only as much as the task needs."],
        map=[("The librarian at the desk", "A plain LLM: answers from the prompt and its training"),
             ("The phone and the calculator", "Tools: functions the model can ask your code to run"),
             ("Walking to the stacks and back", "One loop step: act, then observe the result"),
             ("Checking again until it's answered", "Repeating the loop toward the goal"),
             ("Someone telling them to stop", "Your code's guards: step limits, budgets")],
        fig=compare(("Chatbot: one shot",
                     ["Reads the prompt once and replies",
                      "Knows only its training data and what you pasted",
                      "“What's 18% of this invoice?” → a guess at the number"], "b"),
                    ("Agent: a loop with tools",
                     ["Decides an action, runs a tool, reads the result, decides again",
                      "Can look things up and check its own work",
                      "Same question → calls a calculator, then answers with the exact figure"], "a"),
                    "Chatbot versus agent on the same request",
                    verdict="Autonomy is a dial: plain LLM, tool-augmented, agent loop, then multi-agent. Turn it only as far as the task needs."),
        cap="The difference is the loop. The agent's answer is built from tool results it observed, not from one pass over the prompt.",
        line="A chatbot talks once; an agent loops through tools until the job is done."),
    "4.2": dict(
        plain=["A tool is a function the model is allowed to ask for, such as get_weather(city).",
               "You describe each tool with a name, a plain description and typed parameters: the tool schema.",
               "The model never runs anything itself. It replies with a tool call: the tool's name plus arguments.",
               "Your code checks the arguments, runs the function, and sends the result back as a new message.",
               "Then the model uses that result to write its answer."],
        map=[("The request slip", "The tool call: a name plus JSON arguments"),
             ("The library catalogue the kid reads", "The tool schemas you send with the request"),
             ("The librarian checking the slip", "Your code validating every argument"),
             ("Fetching the book from the back room", "Running the real function or API"),
             ("Handing the book over", "Appending the tool result to the conversation")],
        fig=flow([("Send messages + tool schemas", "name, description, typed parameters", "c"),
                  ("Model returns a tool call", "get_weather {“city”: “Paris”}", "a"),
                  ("Your code checks and runs it", "the model can't run anything", "k"),
                  ("Append the tool result", "“Paris: 18°C, clear”", "b"),
                  ("Model writes the answer", "“It's 18°C and clear in Paris.”", "g")],
                 "The tool-calling round trip"),
        cap="Steps 1, 2 and 5 are model calls you make; steps 3 and 4 are your code. The lesson's own get_weather example is used for every value shown.",
        line="The model fills in a request slip; your code checks it, does the work and hands back the result."),
    "4.3": dict(
        plain=["Real tasks need several tool calls, where each one depends on the last.",
               "The agent loop runs in steps. In each step the model thinks, then calls a tool or gives a final answer.",
               "The tool's result is added to the conversation, and the loop goes round again.",
               "Interleaving the reasoning with the actions like this is called ReAct (reason + act).",
               "A step limit stops the loop if the model never finishes, because it will happily try forever."],
        map=[("Thinking “she likes the park”", "The model's reasoning about the next move"),
             ("Going to look", "A tool call (the action)"),
             ("Seeing nothing there", "The tool result (the observation), appended to the messages"),
             ("Choosing the next place from what you saw", "The next step is conditioned on every observation so far"),
             ("Giving up after an hour", "The guard your code adds: max_steps")],
        fig=loop_svg(),
        cap="Each lap is one step. The loop has two ways out: the model gives an answer with no tool call (green), or the budget check fails and your code stops it (red). The second exit exists only if you write it.",
        play=("agentloop", "Press Step to walk a scripted run, one stage at a time. Lower the step budget below 4 and the guard stops the run before it can answer."),
        line="Think, act, look at the result, repeat, and always have a step limit."),
    "4.4": dict(
        plain=["A purely reactive agent takes one step at a time and hopes it ends up somewhere good.",
               "On big goals that wanders.",
               "Planning means writing down the sub-tasks first, then working through them.",
               "Plan-then-execute makes the list once. Plan-and-reflect checks after each step and changes the list when something surprises it.",
               "A plan is also easy to inspect, so you can catch impossible steps before anything runs."],
        map=[("The packing checklist", "The plan: 2 to 5 ordered sub-tasks, as structured data"),
             ("Packing and ticking items off", "Executing each sub-task, often with the 4.3 agent loop"),
             ("Adding an umbrella when it rains", "Plan-and-reflect: replanning after a surprise"),
             ("Checking the list makes sense", "Validating the plan before running it")],
        fig=flow([("Goal", "“Write a short brief comparing two products”", "a"),
                  ("Make the plan", "2 to 5 ordered steps, as JSON", "c"),
                  ("Check the plan", "every step possible? every tool real?", "k"),
                  ("Run the next step", "with the 4.3 agent loop", "b"),
                  ("Reflect", "done? on track? if a page is missing, change the plan", "p")],
                 "Plan-and-reflect: plan, check, run a step, reflect, repeat",
                 loop=(4, 2, "next step, or a revised plan (checked again)")),
        cap="Plan-then-execute is boxes 1 to 4 with the steps run in order. Plan-and-reflect adds box 5 and the loop: after each step the agent checks progress and may rewrite the rest of the plan. The example goal is illustrative.",
        line="Write the to-do list first, then do it, and change the list when reality surprises you."),
    "4.5": dict(
        plain=["A model only remembers what is in its context window right now. That is short-term memory.",
               "Long chats overflow the window, so older turns get squeezed into a short summary.",
               "Long-term memory lives outside the model, in a database or a vector store.",
               "When a new question comes in, the agent looks up the relevant memories and adds them to the prompt.",
               "That lookup is RAG, pointed at the agent's own history."],
        map=[("What you can hold in your head in class", "Short-term memory: the context window"),
             ("Writing key points in the notebook", "Summarising older turns to free tokens"),
             ("The labelled index at the back", "Vector memory: stored facts, retrieved by similarity"),
             ("“Last time, she preferred email”", "Episodic memory: a specific past event"),
             ("“Her timezone is IST”", "Semantic memory: a distilled fact")],
        fig=stack([("Recent turns, word for word", "the last few messages, kept as they are", "a"),
                   ("Running summary of older turns", "compressed when the chat passes a token budget", "c"),
                   ("Retrieved long-term memories", "top few facts from the vector store, e.g. “timezone: IST”", "k"),
                   ("Writing back", "after the turn, save new facts and summaries for next time", "g")],
                  "How an agent's context is assembled from short-term and long-term memory",
                  enter="a new message arrives", leave="one prompt that fits the context window",
                  blocked={2: "an old, wrong memory is trusted as much as a new one: date and update memories"}),
        cap="Layers 1 to 3 are what the model sees on this turn. Layer 4 is the deliberate write step; nothing is remembered unless your code saves it.",
        line="Keep recent words, summarise the old ones, and look up the rest when you need it."),
    "4.6": dict(
        plain=["MCP (Model Context Protocol) is a standard way to plug tools and data into AI apps.",
               "Without it, every app needs its own hand-written connector for every system.",
               "With it, you wrap a system once as an MCP server, and any MCP-ready app can use it.",
               "A server can offer tools to call, resources to read and prompt templates.",
               "In the current spec (dated 2026-07-28), every request stands on its own: there is no start-up handshake."],
        map=[("The standard socket in the wall", "The MCP protocol: JSON-RPC over stdio or Streamable HTTP"),
             ("Your house's wiring", "The MCP client inside the host app"),
             ("A lamp or a charger", "An MCP server wrapping one system (orders, a wiki, Postgres)"),
             ("Plugging in any brand", "Discovery: tools/list returns each tool's schema"),
             ("Switching it on", "tools/call: the client asks the server to run a tool")],
        fig=mcp_svg(),
        cap="Time runs downward. Steps 1 to 3 are discovery; steps 4 to 9 are one tool call and its way back. The model only ever talks to the host; the server's own code is what touches the real system. The order data is illustrative.",
        play=("mcpflow", "Press Step to move one tool call across the host, the client, the server and the order system, and back."),
        line="MCP is a standard plug: wrap a system once as a server, and every compatible AI app can use it."),
    "4.7": dict(
        plain=["One agent with a dozen tools and roles gets confused.",
               "A multi-agent system splits the work between focused specialists.",
               "An orchestrator decides who does what and combines the results.",
               "A handoff passes the job, and the context it needs, from one agent to another.",
               "It adds cost and new ways to fail, so use it only when one agent really isn't enough."],
        map=[("The group leader", "The orchestrator (or supervisor)"),
             ("The kid who researches", "A specialist: narrow role, its own prompt and tools"),
             ("Passing your notes to the writer", "A handoff: control plus the context it needs"),
             ("Vague instructions, so everyone guessed", "A thin handoff message: agents only know what they were sent")],
        fig=fan(("Orchestrator", "classifies the request, picks a specialist", "a"),
                [("Billing specialist", "tools: invoices, refunds", "k"),
                 ("Technical specialist", "tools: logs, docs search", "c"),
                 ("Shipping specialist", "tools: order lookup, carrier tracking", "d"),
                 ("No match", "hand off to a human", "w")],
                "The router pattern: one orchestrator, several specialists"),
        cap="This is the router, the simplest of the lesson's four patterns. Each arrow is a handoff, and the specialist sees only what travels along it. Pipelines, supervisors and parallel fan-outs reuse the same parts.",
        line="Split a big job between focused specialists, with one leader who hands out the work clearly."),
    "4.8": dict(
        plain=["An agent is software with tools and freedom, so it can fail in costly ways a chatbot can't.",
               "It can loop forever, call a tool with bad arguments, run up a bill, or do something you can't undo.",
               "A guard is a rule in your code that limits what the agent may do.",
               "You stack several guards, so when one misses, another catches it. This is called defence in depth.",
               "The guards must live in the system, not in the prompt, because a prompt can be talked out of them."],
        map=[("Looking up balances alone", "Safe, read-only tools the agent may call freely"),
             ("The manager's signature for big withdrawals", "Human-in-the-loop approval for risky actions"),
             ("The cash drawer limit", "Budgets and timeouts: tokens, cost, wall-clock time"),
             ("Only the keys the trainee needs", "Least privilege: each agent gets only its tools"),
             ("Every transaction in the log", "Observability: log every step")],
        fig=stack([("Step limit", "bound the loop, e.g. max_steps = 6", "a"),
                   ("Argument validation", "check every tool input before running it", "c"),
                   ("Budget and timeout", "cap tokens, cost and wall-clock time", "k"),
                   ("Human approval", "send_email, delete_file, charge_card wait for a person", "p"),
                   ("Least privilege + logs", "only the tools this agent needs; every step recorded", "g")],
                  "Guards stacked around an agent's actions",
                  enter="the agent proposes an action", leave="the action runs, or a person is asked",
                  blocked={0: "stops a stuck loop", 1: "stops an invented order ID", 2: "stops a runaway bill",
                           3: "stops an irreversible mistake", 4: "limits the damage, and shows what happened"}),
        cap="Every proposed action passes all five layers, and no single layer is trusted alone. On wider screens, a red note beside each layer names the failure it catches.",
        line="Give an agent limits it can't argue with: step caps, checks, budgets, approvals and a log."),
}
