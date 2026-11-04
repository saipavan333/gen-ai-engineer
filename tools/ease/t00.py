"""Pass 2, Section 0: Start Here."""
from ease.kit import arrow, esc, fan, flow, path_arrow, raw, rect, svg, text, wrap


def fstring_svg():
    """Values flow into the {slots} of an f-string and come out as one finished prompt (the page's own example)."""
    out = []
    for W, cls in ((760, "ez-wide"), (360, "ez-tall")):
        nw = W < 400
        body = text(14, 22, "Two variables", "s m", "start")
        vals = [("topic", '"the water cycle"'), ("grade", "5")]
        xs = []
        for i, (k, v) in enumerate(vals):
            x = 14 + i * (W / 2 - 4) if not nw else (14 if i == 0 else 228)
            y = 34
            w = W / 2 - 30 if not nw else (206 if i == 0 else 118)
            body += rect(x, y, w, 40, "c") + text(x + 10, y + 26, f"{k} = {v}", "mono", "start", 13 if nw else None)
            xs.append((x + w / 2, y + 40))
        ty = 120
        tmpl = ["f\"Explain ", "{topic}", " to a grade-", "{grade}", " student in 3 sentences.\""]
        # lay the template out as pieces; slots highlighted
        x, y, lh = 14, ty, 40
        slot_pos = {}
        rows_w = W - 28
        for piece in tmpl:
            w = len(piece) * (8.6 if not nw else 8.1) + 10
            if x + w > 14 + rows_w:
                x, y = 14, y + lh
            tone = "k" if piece.startswith("{") else "b"
            body += rect(x, y, w, 32, tone, rx=6) + text(x + w / 2, y + 21, piece, "mono", size=14)
            if piece.startswith("{"):
                slot_pos[piece[1:-1]] = (x + w / 2, y) if y == ty else (x + 38 + 0 * w, y)
            x += w + 4
        for (k, _), (vx, vy) in zip(vals, xs):
            sx, sy = slot_pos[k]
            if sy > ty:  # slot wrapped to a lower row: go round the left margin instead of through the first row
                body += path_arrow([(vx, vy + 2), (vx, vy + 14), (6, vy + 14), (6, sy + 16), (sx - 38, sy + 16)], "ac")
            else:
                body += path_arrow([(vx, vy + 2), (vx, (vy + ty) / 2), (sx, (vy + ty) / 2), (sx, sy - 3)], "ac")
        y += 32 + 34
        body += arrow(W / 2, y - 30, W / 2, y - 6)
        res = wrap("Explain the water cycle to a grade-5 student in 3 sentences.", W - 50, 15)
        body += rect(14, y, W - 28, 20 + 20 * len(res), "g")
        for i, r in enumerate(res):
            body += text(26, y + 26 + i * 20, r, "", "start")
        body += text(14, y + 46 + 20 * len(res), "The result is one ordinary string: a prompt ready to send.", "s ok-t", "start")
        out.append(svg(W, y + 58 + 20 * len(res), body, "Variables flow into the slots of an f-string", cls))
    return raw(*out)


LESSONS = {
    "0.1": dict(
        plain=["This course takes you from zero to building real AI products that people can trust.",
               "It has 17 tracks, like the chapters of a book, in a fixed order.",
               "Every lesson starts simple, with a picture, and then goes deeper.",
               "Each one ends with something to run, a quiz, exercises and interview questions.",
               "The only test: could you explain it to a friend, and use it at work?"],
        pic="Think of a cookbook that teaches you to cook, not just a pile of recipes. Early chapters teach knife skills and heat, later ones build whole meals on top. Each recipe has the same steps: read it, watch how it is done, cook it yourself, then taste.",
        map=[("The chapters, in order", "The 17 tracks: each builds on the ones before it"),
             ("Reading the recipe", "Start here, the everyday picture and the diagram"),
             ("The chef's notes in the margin", "Going deeper: the full technical detail"),
             ("Cooking it yourself", "Typing and running the lab code, not copy-pasting it"),
             ("Tasting the dish", "The quiz and the 'could I explain this?' test")],
        breaks="You can safely skip to the dessert chapter of a cookbook. Here, later tracks lean on earlier ones, so skipping Tracks 1 and 2 leaves gaps that show up later.",
        fig=flow([("Start here", "plain words + a picture", "a"), ("See how it works", "diagram, try-it", "c"),
                  ("Going deeper", "the real detail", "d"), ("Run it", "type the lab code yourself", "k"),
                  ("Check yourself", "quiz, then explain it out loud", "g")],
                 "How to work through one lesson", loop=(4, 0, "can't explain it yet? loop back, it's cheap")),
        cap="The same five steps in every lesson. The loop is the point: if you can't explain the idea simply, go round again before moving on.",
        line="Go in order, run the code yourself, and only move on when you can explain the lesson to a friend."),
    "0.2": dict(
        plain=["To learn AI you need somewhere to run code.",
               "Google Colab is a free website that runs Python code for you.",
               "You type code into a box called a cell and press Shift + Enter.",
               "The code runs on one of Google's computers, and the answer appears right under the cell.",
               "There is nothing to install and no credit card to enter."],
        pic="Colab is like a library's computer room. You show your library card, sit at a machine that isn't yours, type your work, and the result comes out right in front of you. Your work is saved in your locker so you can come back tomorrow.",
        map=[("Your library card", "A free Google account"),
             ("The library's computer", "Google's machine that actually runs your code"),
             ("One request you type in", "A cell: a small chunk of code you run on its own"),
             ("The printout you get back", "The output shown under the cell"),
             ("Your locker", "Google Drive, where Colab saves the notebook")],
        breaks="A library computer is yours for the whole visit. Colab's free GPU (a fast chip for AI work) is shared: Google limits how long you can use it, and at busy times one may not be free.",
        fig=flow([("You type a cell", "print(\"hello\")", "c"), ("Shift + Enter", "send it to run", "a"),
                  ("Google's machine runs it", "nothing runs on your laptop", "d"), ("Output appears", "right under the cell", "g"),
                  ("Saved to Drive", "close the tab, come back later", "k")],
                 "How a Colab cell runs"),
        cap="Your browser only shows the notebook. The work happens on Google's computer, which is why a cheap laptop is enough for this course.",
        line="Colab is a free notebook in your browser: type a cell, press Shift + Enter, and Google's computer runs it for you."),
    "0.3": dict(
        plain=["Python is the language most AI tools speak.",
               "You only need a small slice of it to start: about eight ideas.",
               "The most important one is the f-string, which drops values into the middle of text.",
               "That matters because a prompt to an AI model is just text.",
               "Learn these eight and you can read every example in this course."],
        pic="Think of a kitchen. Ingredients sit in labelled jars, some jars stand in a row on a shelf, and the spice rack has a name on every slot. A recipe card turns ingredients into a dish, you repeat a step for every jar on the shelf, and you only add chilli if someone likes it hot.",
        map=[("A labelled jar", "A variable: a name stuck on a value, like model_name = \"qwen2.5:7b\""),
             ("A row of jars on a shelf", "A list: items in order, like a list of chunks"),
             ("The spice rack with named slots", "A dictionary: look a value up by its key, like reply[\"text\"]"),
             ("A recipe card", "A function: give it inputs, get a result back"),
             ("'For every jar' and 'only if it's hot'", "A for loop and an if statement")],
        breaks="A jar holds one thing in one place. In Python two names can point at the same list, so changing it through one name changes what the other name sees too.",
        fig=fstring_svg(),
        cap="The f-string from this lesson, taken apart: two variables on top, the template in the middle, the finished prompt below. Each {name} in the template is a slot, and Python fills it with that variable's value when the line runs.",
        play=("fstring", "Pick a topic and move the grade slider. The template stays the same; the finished prompt changes. This is how you build prompts from data."),
        line="A few small Python ideas, above all the f-string, are enough to build prompts and read AI code."),
    "0.4": dict(
        plain=["Real AI code keeps doing the same few small moves.",
               "It turns one list into another, like raw documents into clean chunks.",
               "It reads a field out of a model's reply, which usually arrives as JSON (text shaped like a dictionary).",
               "It builds a prompt from pieces, and it survives a call that goes wrong.",
               "This lesson teaches those moves, and then real code stops looking scary."],
        pic="Picture a post office sorting room. Every letter goes through the same stamping machine, and letters that are too small drop into a reject bin. Clerks open envelopes and copy one box off the form inside. A torn letter goes to a 'problems' tray instead of stopping the whole line.",
        map=[("The stamping machine with a reject bin", "A list comprehension with an if filter"),
             ("Opening the envelope and reading the form", "json.loads() turns the reply text into a dictionary"),
             ("Copying one box, or writing 'blank' if it's empty", "reply.get(\"answer\", \"\"): a default instead of a crash"),
             ("The 'problems' tray", "try / except: catch the error and carry on")],
        breaks="A torn letter is obvious at a glance. Broken JSON from a model looks like normal text until json.loads() fails, so you only find out by trying to parse it.",
        fig=fan(("A model reply arrives", "it is just text", "c"),
                [("It is valid JSON", "json.loads() gives a dict; .get() reads the field you need", "g"),
                 ("A field is missing", ".get(\"answer\", \"\") returns your default instead of a KeyError", "k"),
                 ("The JSON is broken", "json.loads() raises; except catches it, then retry or use a fallback", "w")],
                "Three things a model reply can be, and the Python move that handles each"),
        cap="Most crashes in early AI code come from assuming the reply is perfect. These three moves cover the three cases.",
        line="Expect the model's reply to be messy, and use .get(), try/except and comprehensions to handle it calmly."),
    "0.5": dict(
        plain=["Reading code is not the same as writing it.",
               "These six short drills move the patterns from 0.3 and 0.4 into your fingers.",
               "Each one is a small task you will meet again, like a tiny chunker or a keyword search.",
               "Try each drill yourself before you open the solution.",
               "Errors are normal: read the last line of the message, fix it, and run again."],
        pic="Drills are like practising scales on a piano. You play slowly, hit a wrong note, play it again, and only then listen to your teacher play it. Later, a real song uses the same scale and your fingers already know it.",
        map=[("Playing the scale slowly yourself", "Typing your own attempt in a Colab cell"),
             ("Hitting a wrong note and replaying", "Reading the error's last line, fixing it, rerunning"),
             ("Listening to the teacher's version", "Opening the solution after you tried"),
             ("The song that uses the scale", "Later lessons: the chunker in Track 3, keyword search in retrieval")],
        breaks="Scales get repeated for years. One drill done properly is usually enough here, because the real lessons make you use each pattern again.",
        fig=flow([("Read the drill", "know the goal", "c"), ("Type an attempt", "no peeking yet", "a"),
                  ("Run it", "Shift + Enter", "d"), ("Compare with the solution", "is my reasoning the same?", "g")],
                 "The drill loop", loop=(2, 1, "red error? read the last line, fix, run again")),
        cap="The loop between typing and running is where the learning happens. Open the solution only at the end.",
        line="Type it, run it, fix it, and only then look at the answer."),
}
